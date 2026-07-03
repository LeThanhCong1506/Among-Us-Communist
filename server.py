import socket
import select
import random
import pickle
import time
import sys

import rooms

# Debug prints below include Vietnamese room names. Depending on the
# terminal/console codepage this is launched from (or when stdout is
# redirected, e.g. into a subprocess pipe), the default text encoding can be
# a legacy codepage that doesn't cover every Vietnamese character and raises
# UnicodeEncodeError -- which would otherwise crash the whole match server
# over a debug print. Force UTF-8 with a lossy fallback instead.
try:
  sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
  pass

# Larger buffer so we grab as many bytes as possible per recv().
# Message boundaries are handled by length-prefix framing (see frame()/unframe),
# so this value only affects how big each read chunk can be, not correctness.
BUFFERSIZE = 65536
PORT = 4321

# Broadcast the full world snapshot to every client at a fixed rate instead of
# once per received packet. This decouples server outgoing work from how fast
# clients send, which is what lets it scale to ~15 players without melting.
TICK = 0.05  # seconds -> 20 broadcasts per second

# Lobby gate: don't let the game start until enough players have connected,
# then give a short countdown so people can see it coming before it starts.
LOBBY_MIN_PLAYERS = 2  # keep at 2 for local testing; raise to 5+ for classroom demo if needed
LOBBY_COUNTDOWN_SECONDS = 10
MAX_PLAYERS = 9
SERVER_COLOURS = ["Red", "Blue", "Orange", "Yellow", "Green", "Black", "Brown", "Pink", "Purple", "White"]

def get_local_lan_ip():
  """Same detection method as settings.get_local_lan_ip(), duplicated here
  so server.py doesn't need to import pygame via settings.py."""
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  try:
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]
  except OSError:
    return "127.0.0.1"
  finally:
    s.close()


print("Server Address: " + get_local_lan_ip())


class Minion:
  def __init__(self, player_id):
    self.x = 50
    self.y = 50
    self.sync_img = None
    self.sync_img_index = None
    self.left_img_index = 0
    self.right_img_index = 0
    self.up_img_index = 0
    self.down_img_index = 0
    self.alive_status = True
    self.player_id = player_id
    self.player_colour = None
    self.tasks_completed = 0
    self.sabotagelights_sync = 0
    self.sabotagereactor_sync = 0
    self.victim_id = 0
    self.imposter = False
    self.emergency_sync = 0
    self.voted = None
    self.got_votes = 0
    self.emergency_meeting_img_sync = None
    self.emergency_meeting_img_sync_report = None
    self.victim_id_report = 0
    self.got_reported = False
    self.eject_sync = 0
    self.eject_img = None
    # Deduction-mode fields. None of these travel through 'position update'
    # -- they're set from their own message types and only ever leave via
    # 'deduction state'.
    self.quiz_correct = 0
    self.withdraw_count = 0
    # Imposter-only: +1 per finished question (see 'quiz result'), spent
    # 1-for-1 by 'withdraw done' -- withdrawing has to be earned by
    # visibly doing tasks, not free from the first second of the match.
    self.withdraw_credits = 0
    self.last_progress_ms = None
    # Crewmate-only: set to time.time() + TRACKING_DURATION_SECONDS every
    # time this player finishes a station question (right or wrong -- see
    # the 'quiz result' handler). While in the future, everyone's client
    # already knows this player's live position (it's in every 'player
    # locations' snapshot), so the only NEW information a "tracking" arrow
    # needs is *that this specific crewmate currently has one active* --
    # see tracking_crew in build_deduction_state.
    self.tracking_until = None


minionmap = {}          # player_id -> Minion
conn_buf = {}           # client socket -> bytearray of unparsed received bytes
conn_id = {}            # client socket -> player_id
imposter_ids = []

# Room setup: the first player to join a fresh lobby is the "host" and gets
# to configure these two before the match starts. room_max_players is the
# countdown's target headcount (NOT a join cap -- joining is always allowed
# up to the hard MAX_PLAYERS ceiling). Defaults to LOBBY_MIN_PLAYERS so a
# host who never opens the setup panel keeps the original auto-start-at-2
# behaviour; raise it for a bigger classroom demo. room_imposter_count
# replaces the old fixed "2 if count>=7 else 1" formula -- the host picks
# it directly (default 1), clamped again against the final headcount when
# the match actually starts so there's always at least one crewmate left.
# "Truy Tim Ke Tham Nhung" is a fixed 5-player / 1-imposter deduction game,
# so the room defaults to that shape instead of the old free-form Among Us
# lobby. LOBBY_MIN_PLAYERS stays low so two clients on one machine can still
# smoke-test the flow without needing 5 windows open.
host_id = None
room_max_players = 5
room_imposter_count = 1

# --- Deduction-mode match clock (Phase 2) -----------------------------------
# match_start is set the instant game_started flips True and cleared on the
# next empty-lobby reset. INTERVAL_SECONDS just feeds the clock's "Tx" label
# now (the evidence-board mechanic that originally needed room-history
# tracking per interval was removed -- see the "tracking arrow" mechanic
# below instead); MATCH_TOTAL_SECONDS is when the imposter wins by simply
# outlasting the clock.
INTERVAL_SECONDS = 90
MATCH_TOTAL_SECONDS = 450  # 5 intervals ~= 7.5 minutes
match_start = None
match_ended = False  # one-shot latch so match_end fires exactly once per game

# --- Tracking arrows (replaces the old evidence-board/clue mechanic) --------
# Simpler, faster-paced swap: finishing a station question (any answer) gives
# that crewmate a temporary live arrow to the imposter's position, and
# simultaneously warns the imposter (with an arrow back) exactly which
# crewmate(s) currently have one active, so they can go hide. No secret
# state to maintain server-side -- position is already broadcast to
# everyone via 'player locations'; the only new information is *who
# currently has tracking active*, which is what tracking_crew publishes.
TRACKING_DURATION_SECONDS = 20

# --- Fund withdrawal (Phase 5) -----------------------------------------------
# Imposter's win condition besides outlasting the clock. Client channels
# WITHDRAW_CHANNEL_MS (settings.py) inside Phòng Tài chính before sending
# 'withdraw done' -- the server re-validates role/room/cooldown itself since
# a modified client could otherwise send it from anywhere at any time.
WITHDRAW_COOLDOWN_SECONDS = 90
WITHDRAW_WIN_COUNT = 3
withdraw_last_time = None
withdraw_alert_seq = 0  # incremented per accepted withdrawal; clients dialog once per increase

# --- Idle warning (Phase 5) --------------------------------------------------
# A player who hasn't answered a quiz (or, for the imposter, withdrawn funds)
# in a while gets flagged so everyone can see who's stalling -- last_progress_ms
# is updated by both the 'quiz result' and 'withdraw done' handlers below.
IDLE_THRESHOLD_SECONDS = 100

# --- Server-arbitrated meetings/ejects (Phase 5 hardening) -------------------
# Each client used to time its own 30s meeting countdown and tally votes
# locally -- since votes/emergency_sync already arrive via 'position update'
# (apply_update sets m.voted/m.emergency_sync), the server can just watch
# those and be the single source of truth for who (if anyone) gets ejected,
# instead of two clients potentially reaching slightly different tallies.
MEETING_TIMEOUT_SECONDS = 31  # 30s client-side meeting + 1s grace for late votes
EJECT_TIME_PENALTY_SECONDS = 60
meeting_seq = 0        # highest emergency_sync already turned into a countdown
meeting_deadline = None
eject_seq = 0
eject_result = None    # most recent {"seq","target","was_imposter","time_penalty"}
crew_eject_win = False  # latched True when an eject unmasks the imposter



def frame(data):
  """Prefix a pickled payload with its 4-byte big-endian length."""
  return len(data).to_bytes(4, 'big') + data


def frame_message(message):
  return frame(pickle.dumps(message))


def assign_colour(player_id, preferred):
  used = {m.player_colour for pid, m in minionmap.items()
          if pid != player_id and m.player_colour is not None}
  if preferred in SERVER_COLOURS and preferred not in used:
    return preferred
  for colour in SERVER_COLOURS:
    if colour not in used:
      return colour
  return preferred if preferred in SERVER_COLOURS else SERVER_COLOURS[0]


def apply_update(arr):
  """Apply one 'position update' message from a client into minionmap.

  Field order is IDENTICAL to the original protocol so the game client needs
  no changes to the message contents -- only the transport around it changed.
  """
  player_id = arr[1]
  if player_id == 0:
    return
  if player_id not in minionmap:
    return

  m = minionmap[player_id]
  m.x = arr[2]
  m.y = arr[3]
  m.alive_status = arr[4]
  m.sync_img = arr[5]
  m.sync_img_index = arr[6]
  m.left_img_index = arr[7]
  m.right_img_index = arr[8]
  m.up_img_index = arr[9]
  m.down_img_index = arr[10]
  if m.player_colour is None and arr[11] is not None:
    m.player_colour = assign_colour(player_id, arr[11])
  m.tasks_completed = arr[12]
  m.sabotagelights_sync = arr[13]
  m.sabotagereactor_sync = arr[14]
  m.victim_id = arr[15]
  m.imposter = player_id in imposter_ids
  m.emergency_sync = arr[17]
  m.voted = arr[18]
  m.got_votes = arr[19]
  m.emergency_meeting_img_sync = arr[20]
  m.emergency_meeting_img_sync_report = arr[21]
  m.victim_id_report = arr[22]
  m.got_reported = arr[23]
  m.eject_sync = arr[24]
  m.eject_img = arr[25]


def build_snapshot():
  """Build the full 'player locations' snapshot for every known player.

  Per-player field order is IDENTICAL to the original server, so clients parse
  it exactly as before.
  """
  update = ['player locations']
  for value in minionmap.values():
    update.append([value.player_id, value.x, value.y, value.alive_status,
                   value.sync_img, value.sync_img_index, value.left_img_index,
                   value.right_img_index, value.up_img_index,
                   value.down_img_index, value.player_colour,
                   value.tasks_completed, value.sabotagelights_sync,
                   value.sabotagereactor_sync, value.victim_id, value.imposter,
                   value.emergency_sync, value.voted, value.got_votes,
                   value.emergency_meeting_img_sync,
                   value.emergency_meeting_img_sync_report,
                   value.victim_id_report, value.got_reported, value.eject_sync,
                   value.eject_img])
  return frame(pickle.dumps(update))


def build_lobby_state(count, lobby_deadline, game_started, now):
  """['lobby state', count, min_players, seconds_left_or_None, game_started,
  imposter_ids, host_id, room_max_players, room_imposter_count]"""
  seconds_left = None
  if lobby_deadline is not None and not game_started:
    seconds_left = max(0, int(round(lobby_deadline - now)))
  msg = ['lobby state', count, LOBBY_MIN_PLAYERS, seconds_left, game_started, imposter_ids,
         host_id, room_max_players, room_imposter_count]
  return frame_message(msg)


def build_deduction_state(game_started, now):
  """['deduction state', {dict}] -- everything the deduction-mode client UI
  needs beyond the plain position snapshot. Dict-keyed (not index-based like
  'position update'/'player locations') so new keys can be added in later
  phases without breaking older clients; unknown keys are simply ignored.

  match_end is a one-shot dict once set (imposter disconnected mid-match, or
  too few players remain, or -- once elapsed reaches the total -- the
  imposter outlasted the clock) and stays present every tick afterward, but
  clients act on it once and immediately leave the match loop, so repeats
  are harmless.
  """
  state = {"proto": 2}
  if match_start is not None:
    elapsed = now - match_start
    state["elapsed"] = elapsed
    state["interval"] = int(elapsed // INTERVAL_SECONDS)
    state["total"] = MATCH_TOTAL_SECONDS
  if minionmap:
    state["quiz_correct"] = {pid: m.quiz_correct for pid, m in minionmap.items()}
  if game_started:
    # Tracking arrows: crewmates in this list currently have a live arrow
    # to the imposter (see the 'quiz result' handler); the imposter's
    # client uses this SAME list to know who to point an arrow back at.
    # Position itself needs no new field -- it's already in every
    # 'player locations' snapshot.
    tracking_crew = [pid for pid, m in minionmap.items()
                      if m.tracking_until is not None and now < m.tracking_until]
    if tracking_crew:
      state["tracking_crew"] = tracking_crew
  if withdraw_alert_seq > 0:
    # One-shot: clients remember the last seq they saw and only dialog when
    # this increases, same idiom as the existing *_sync counters in
    # apply_update (night_sync, emergency_sync, etc).
    state["withdraw_alert_seq"] = withdraw_alert_seq
  if game_started:
    # Visible to every player (not just the imposter) so the whole table
    # feels the clock ticking toward WITHDRAW_WIN_COUNT -- only a count, no
    # pid, so nobody's identity leaks through this specifically.
    imposter_minion = next((m for m in minionmap.values() if m.imposter), None)
    state["withdraw_count"] = imposter_minion.withdraw_count if imposter_minion else 0
    # Imposter-only info (their own credit balance, to show "you need to do
    # a task first" on their HUD) -- harmless to send to everyone since it's
    # keyed by pid and nobody but the imposter's own client will find their
    # own pid's entry meaningful.
    if imposter_minion is not None:
      state["withdraw_credits"] = {imposter_minion.player_id: imposter_minion.withdraw_credits}
  if game_started:
    idle_ids = [pid for pid, m in minionmap.items()
                if m.last_progress_ms is not None and now - m.last_progress_ms > IDLE_THRESHOLD_SECONDS]
    if idle_ids:
      state["idle_ids"] = idle_ids
  if eject_result is not None:
    # One-shot by seq (see the meeting-arbitration tick block) -- re-sent
    # every tick like match_end, clients act on it once per increase.
    state["eject_result"] = eject_result
  end = compute_match_end(game_started, now)
  if end is not None:
    state["match_end"] = end
  return frame_message(['deduction state', state])


def compute_match_end(game_started, now):
  """Return {"win_key":..., "imposter_won": bool} once the match should end,
  else None. Only evaluated once game_started so the lobby (where the
  headcount is naturally < 2) never triggers this.
  """
  global match_ended
  if not game_started or match_ended:
    return None
  if crew_eject_win:
    # Set by the meeting-arbitration tick block the instant the ejected
    # target turns out to be the imposter -- checked first since it's
    # already a definitive, freshly-decided outcome.
    match_ended = True
    return {"win_key": "crew_eject", "imposter_won": False}
  if any(m.imposter and m.withdraw_count >= WITHDRAW_WIN_COUNT for m in minionmap.values()):
    match_ended = True
    return {"win_key": "imposter_withdraw", "imposter_won": True}
  if not any(m.imposter for m in minionmap.values()):
    # The imposter's connection dropped (drop_client already removed their
    # minion) -- without them there's no one left to withdraw funds or run
    # out the clock, so the crew wins by default instead of the match
    # hanging forever with no win condition able to fire.
    match_ended = True
    return {"win_key": "imposter_left", "imposter_won": False}
  if len(minionmap) < 2:
    match_ended = True
    return {"win_key": "not_enough_players", "imposter_won": False}
  if match_start is not None and (now - match_start) >= MATCH_TOTAL_SECONDS:
    match_ended = True
    return {"win_key": "imposter_time", "imposter_won": True}
  return None


def drop_client(sock):
  """Remove a disconnected client and its player so ghosts don't pile up.

  If the departing player was the host, hand host_id to whoever joined the
  room earliest among those remaining (dict preserves insertion order) --
  otherwise a host who leaves before opening the setup panel orphans the
  lobby: nobody left could configure room size/imposters and the countdown
  would never fire. Harmless to do unconditionally even mid-match, since
  host_id then only gates the (already-locked) room-config message.
  """
  global host_id
  pid = conn_id.pop(sock, None)
  if pid is not None:
    minionmap.pop(pid, None)
    if pid == host_id:
      host_id = next(iter(minionmap), None)
  conn_buf.pop(sock, None)
  try:
    sock.close()
  except Exception:
    pass


def main():
  global imposter_ids, host_id, room_max_players, room_imposter_count
  global match_start, match_ended
  global withdraw_last_time, withdraw_alert_seq
  global meeting_seq, meeting_deadline, eject_seq, eject_result, crew_eject_win
  server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  server.bind(('', PORT))
  server.listen(16)
  server.setblocking(False)

  clients = [server]
  last_tick = time.time()
  lobby_deadline = None   # timestamp the countdown ends; None = not counting down
  game_started = False    # one-way latch: once the countdown finishes, stays True

  while True:
    # Wake up at least every TICK seconds so broadcasts stay on schedule even
    # when no client is sending.
    try:
      rlist, _, _ = select.select(clients, [], [], TICK)
    except Exception:
      rlist = []

    for sock in rlist:
      if sock is server:
        # New connection: register a player unless the lobby is full or the
        # match has already started.
        try:
          conn, addr = server.accept()
        except Exception:
          continue
        deny_reason = None
        if game_started:
          deny_reason = 'started'
        elif len(minionmap) >= MAX_PLAYERS:
          # The hard ceiling is always MAX_PLAYERS, not room_max_players --
          # the latter defaults low (LOBBY_MIN_PLAYERS) so a host who hasn't
          # opened the setup panel still gets the old auto-start-at-2
          # behaviour, and that must not also lock out the 3rd+ joiner.
          deny_reason = 'full'
        if deny_reason is not None:
          try:
            conn.sendall(frame_message(['join denied', deny_reason]))
            time.sleep(0.05)
          except Exception:
            pass
          conn.close()
          continue
        conn.setblocking(False)
        clients.append(conn)
        conn_buf[conn] = bytearray()
        is_first_player = not minionmap
        player_id = random.randint(1000, 1000000)
        while player_id in minionmap:
          player_id = random.randint(1000, 1000000)
        minionmap[player_id] = Minion(player_id)
        conn_id[conn] = player_id
        if is_first_player:
          host_id = player_id
        continue

      # Existing client: read whatever is available.
      try:
        data = sock.recv(BUFFERSIZE)
      except Exception:
        data = b''
      if not data:
        if sock in clients:
          clients.remove(sock)
        drop_client(sock)
        continue

      buf = conn_buf[sock]
      buf.extend(data)
      # Pull out every complete length-prefixed frame currently in the buffer.
      while len(buf) >= 4:
        n = int.from_bytes(buf[:4], 'big')
        if len(buf) < 4 + n:
          break
        msg = bytes(buf[4:4 + n])
        del buf[:4 + n]
        try:
          arr = pickle.loads(msg)
          if arr and arr[0] == 'hello':
            pid = conn_id.get(sock)
            if pid in minionmap:
              preferred = arr[1] if len(arr) > 1 else None
              minionmap[pid].player_colour = assign_colour(pid, preferred)
              sock.sendall(frame_message(['id update', pid, minionmap[pid].player_colour]))
          elif arr and arr[0] == 'position update':
            apply_update(arr)
          elif arr and arr[0] == 'room config':
            pid = conn_id.get(sock)
            if pid is not None and pid == host_id and not game_started:
              room_max_players = max(LOBBY_MIN_PLAYERS, min(MAX_PLAYERS, int(arr[1])))
              # Fixed 5-player / 1-imposter deduction game -- imposter count
              # is no longer host-configurable, arr[2] is ignored.
              room_imposter_count = 1
          elif arr and arr[0] == 'quiz result':
            # ['quiz result', pid, question_id, is_correct] -- question_id
            # isn't tracked server-side (nothing needs it). A CREWMATE only
            # gets the tracking arrow on a CORRECT answer -- a wrong one
            # still counts as "progress" for the idle timer, but doesn't
            # reveal the imposter's direction. The imposter's own
            # withdraw-credit side of this (further down) still counts any
            # attempt, right or wrong, since blending in is about visibly
            # participating, not being right.
            pid = arr[1]
            is_correct = arr[3]
            minion = minionmap.get(pid)
            if minion is not None:
              # time.time(), not the tick-loop's `now` -- this handler runs
              # in the per-socket receive loop, which executes before `now`
              # is computed for this tick (and may run several times between
              # ticks), so `now` isn't in scope here.
              now_ts = time.time()
              minion.last_progress_ms = now_ts
              if is_correct:
                minion.quiz_correct += 1
              if not minion.imposter and is_correct:
                minion.tracking_until = now_ts + TRACKING_DURATION_SECONDS
              elif minion.imposter:
                # Withdrawing has to be earned: 1 finished question (right
                # or wrong -- blending in is what counts) = 1 withdraw
                # credit, 1:1, so the imposter can't just camp Phòng Tài
                # chính from minute one.
                minion.withdraw_credits += 1
          elif arr and arr[0] == 'withdraw done':
            # ['withdraw done', pid] -- the client only sends this after
            # channeling WITHDRAW_CHANNEL_MS (settings.py) inside Phòng Tài
            # chính without moving, but a modified client could send it from
            # anywhere at any time, so the server re-validates role, current
            # room (from the last 'position update'), and cooldown itself.
            pid = arr[1]
            minion = minionmap.get(pid)
            now_ts = time.time()
            on_cooldown = (withdraw_last_time is not None
                           and now_ts - withdraw_last_time < WITHDRAW_COOLDOWN_SECONDS)
            in_finance_room = minion is not None and rooms.room_at(minion.x, minion.y) == rooms.FINANCE_ROOM
            has_credit = minion is not None and minion.withdraw_count < minion.withdraw_credits
            if (minion is not None and minion.imposter and in_finance_room and not on_cooldown
                and has_credit):
              minion.withdraw_count += 1
              minion.last_progress_ms = now_ts
              withdraw_last_time = now_ts
              withdraw_alert_seq += 1
        except Exception:
          pass

    # Fixed-rate broadcast to all clients.
    now = time.time()
    if now - last_tick >= TICK:
      last_tick = now

      count = len(minionmap)
      if count == 0:
        # Everyone left -- reset so the next group to join gets a fresh
        # lobby/countdown instead of the server "remembering" a past game
        # started and skipping straight to gameplay for whoever connects next.
        game_started = False
        lobby_deadline = None
        imposter_ids = []
        host_id = None
        room_max_players = 5
        room_imposter_count = 1
        match_start = None
        match_ended = False
        withdraw_last_time = None
        withdraw_alert_seq = 0
        meeting_seq = 0
        meeting_deadline = None
        eject_seq = 0
        eject_result = None
        crew_eject_win = False
      elif not game_started:
        # room_max_players doubles as the match's target size: the host sets
        # how many are expected (default MAX_PLAYERS), and the countdown
        # waits for exactly that many rather than a separate fixed minimum.
        if lobby_deadline is None and count >= room_max_players:
          lobby_deadline = now + LOBBY_COUNTDOWN_SECONDS
        elif lobby_deadline is not None and count < room_max_players:
          lobby_deadline = None  # someone left before the countdown finished -- cancel it
        elif lobby_deadline is not None and now >= lobby_deadline:
          ids = list(minionmap.keys())
          # Host-configured count (default 1), clamped so at least one
          # crewmate always remains regardless of what was configured.
          imposter_count = max(1, min(room_imposter_count, count - 1))
          imposter_ids = random.sample(ids, min(imposter_count, len(ids)))
          for pid, minion in minionmap.items():
            minion.imposter = pid in imposter_ids
            # Idle clock starts at the match, not whenever they happened to
            # join the lobby -- otherwise someone who sat in the lobby a
            # while looks idle from frame one of actual gameplay.
            minion.last_progress_ms = now
          game_started = True
          match_start = now

      if game_started:
        # A meeting starts the instant any minion's emergency_sync rises
        # above every meeting we've already started a countdown for --
        # covers both the emergency-button and report-body triggers, since
        # both increment emergency_sync client-side before this arrives.
        current_max_emerg = max((m.emergency_sync for m in minionmap.values()), default=0)
        if current_max_emerg > meeting_seq and meeting_deadline is None:
          meeting_seq = current_max_emerg
          meeting_deadline = now + MEETING_TIMEOUT_SECONDS
        if meeting_deadline is not None and now >= meeting_deadline:
          vote_counts = {}
          skip_votes = 0
          for m in minionmap.values():
            if not m.alive_status:
              continue
            v = m.voted
            if v == "SKIP":
              skip_votes += 1
            elif isinstance(v, int):
              target_minion = minionmap.get(v)
              if target_minion is not None and target_minion.alive_status:
                vote_counts[v] = vote_counts.get(v, 0) + 1
          target = None
          if vote_counts:
            highest = max(vote_counts.values())
            winners = [pid for pid, c in vote_counts.items() if c == highest]
            if len(winners) == 1 and highest > skip_votes:
              target = winners[0]
          was_imposter = False
          time_penalty = 0
          if target is not None:
            target_minion = minionmap.get(target)
            if target_minion is not None:
              was_imposter = target_minion.imposter
              target_minion.alive_status = False
              if was_imposter:
                crew_eject_win = True
              else:
                match_start -= EJECT_TIME_PENALTY_SECONDS
                time_penalty = EJECT_TIME_PENALTY_SECONDS
          eject_seq += 1
          eject_result = {"seq": eject_seq, "target": target, "was_imposter": was_imposter,
                           "time_penalty": time_penalty}
          meeting_deadline = None

      payload = (build_snapshot() + build_lobby_state(count, lobby_deadline, game_started, now)
                 + build_deduction_state(game_started, now))
      for c in list(clients):
        if c is server:
          continue
        try:
          c.sendall(payload)
        except Exception:
          if c in clients:
            clients.remove(c)
          drop_client(c)


if __name__ == '__main__':
  main()
