import socket
import select
import random
import pickle
import time

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


minionmap = {}          # player_id -> Minion
conn_buf = {}           # client socket -> bytearray of unparsed received bytes
conn_id = {}            # client socket -> player_id
imposter_ids = []

# Room setup: the first player to join a fresh lobby is the "host" and gets
# to configure these two before the match starts. room_max_players is the
# countdown's target headcount (NOT a join cap -- joining is always allowed
# up to the hard MAX_PLAYERS ceiling). Defaults to LOBBY_MIN_PLAYERS so a
# host who never opens the setup panel keeps the original auto-start-at-2
# behaviour; raise it for a bigger classroom demo.
host_id = None
room_max_players = LOBBY_MIN_PLAYERS
room_bot_count = 0


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
  imposter_ids, host_id, room_max_players, room_bot_count]"""
  seconds_left = None
  if lobby_deadline is not None and not game_started:
    seconds_left = max(0, int(round(lobby_deadline - now)))
  msg = ['lobby state', count, LOBBY_MIN_PLAYERS, seconds_left, game_started, imposter_ids,
         host_id, room_max_players, room_bot_count]
  return frame_message(msg)


def drop_client(sock):
  """Remove a disconnected client and its player so ghosts don't pile up."""
  pid = conn_id.pop(sock, None)
  if pid is not None:
    minionmap.pop(pid, None)
  conn_buf.pop(sock, None)
  try:
    sock.close()
  except Exception:
    pass


def main():
  global imposter_ids, host_id, room_max_players, room_bot_count
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
              room_bot_count = max(0, min(9, int(arr[2])))
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
        room_max_players = LOBBY_MIN_PLAYERS
        room_bot_count = 0
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
          imposter_count = 2 if count >= 7 else 1
          imposter_ids = random.sample(ids, min(imposter_count, len(ids)))
          for pid, minion in minionmap.items():
            minion.imposter = pid in imposter_ids
          game_started = True

      payload = build_snapshot() + build_lobby_state(count, lobby_deadline, game_started, now)
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
