export const createWebSocket = (onMessage) => {
  const ws = new WebSocket("ws://localhost:8000/ws");

  ws.onmessage = (e) => {
    const data = JSON.parse(e.data);
    onMessage(data);
  };

  return ws;
};