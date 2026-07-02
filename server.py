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
LOBBY_MIN_PLAYERS = 2
LOBBY_COUNTDOWN_SECONDS = 10

print("Server Address: " + socket.gethostbyname(socket.gethostname()))


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
    self.eject_sync = False
    self.eject_img = None


minionmap = {}          # player_id -> Minion
conn_buf = {}           # client socket -> bytearray of unparsed received bytes
conn_id = {}            # client socket -> player_id


def frame(data):
  """Prefix a pickled payload with its 4-byte big-endian length."""
  return len(data).to_bytes(4, 'big') + data


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
  m.player_colour = arr[11]
  m.tasks_completed = arr[12]
  m.sabotagelights_sync = arr[13]
  m.sabotagereactor_sync = arr[14]
  m.victim_id = arr[15]
  m.imposter = arr[16]
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
  """['lobby state', connected_count, min_players, seconds_left_or_None, game_started]"""
  seconds_left = None
  if lobby_deadline is not None and not game_started:
    seconds_left = max(0, int(round(lobby_deadline - now)))
  msg = ['lobby state', count, LOBBY_MIN_PLAYERS, seconds_left, game_started]
  return frame(pickle.dumps(msg))


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
        # New connection: register a player and hand it its id.
        try:
          conn, addr = server.accept()
        except Exception:
          continue
        conn.setblocking(False)
        clients.append(conn)
        conn_buf[conn] = bytearray()
        player_id = random.randint(1000, 1000000)
        minionmap[player_id] = Minion(player_id)
        conn_id[conn] = player_id
        try:
          conn.sendall(frame(pickle.dumps(['id update', player_id])))
        except Exception:
          clients.remove(conn)
          drop_client(conn)
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
          apply_update(pickle.loads(msg))
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
      elif not game_started:
        if lobby_deadline is None and count >= LOBBY_MIN_PLAYERS:
          lobby_deadline = now + LOBBY_COUNTDOWN_SECONDS
        elif lobby_deadline is not None and count < LOBBY_MIN_PLAYERS:
          lobby_deadline = None  # someone left before the countdown finished -- cancel it
        elif lobby_deadline is not None and now >= lobby_deadline:
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
