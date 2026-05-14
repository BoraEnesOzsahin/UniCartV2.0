(() => {
  const root = document.querySelector('[data-chat-root]');
  if (!root) return;

  const conversationId = root.getAttribute('data-conversation-id');
  const currentUserId = Number(root.getAttribute('data-current-user-id'));

  const messagesEl = document.getElementById('chat-messages');
  const formEl = document.getElementById('chat-form');
  const inputEl = document.getElementById('chat-input');
  const warningEl = document.getElementById('chat-warning');
  const imageFormEl = document.getElementById('chat-image-form');

  const scrollToBottom = () => {
    if (!messagesEl) return;
    messagesEl.scrollTop = messagesEl.scrollHeight;
  };

  const showWarning = (text) => {
    if (!warningEl) return;
    if (!text) {
      warningEl.classList.add('hidden');
      warningEl.textContent = '';
      return;
    }
    warningEl.textContent = text;
    warningEl.classList.remove('hidden');
  };

  const escapeHtml = (s) => {
    const div = document.createElement('div');
    div.textContent = s;
    return div.innerHTML;
  };

  const renderMessage = (m) => {
    const isMine = Number(m.sender_id) === currentUserId;
    const wrap = document.createElement('div');
    wrap.className = `flex ${isMine ? 'justify-end' : 'justify-start'}`;

    const bubble = document.createElement('div');
    bubble.className = `max-w-[85%] md:max-w-[70%] rounded-2xl px-4 py-3 border bg-white ${isMine ? 'border-orange-100' : 'border-gray-100'}`;

    if (m.image_url) {
      const img = document.createElement('img');
      img.src = m.image_url;
      img.alt = 'Shared image';
      img.className = 'rounded-xl max-h-72 w-auto mb-2';
      bubble.appendChild(img);
    }

    if (m.text) {
      const p = document.createElement('p');
      p.className = 'text-sm text-gray-800 whitespace-pre-wrap break-words';
      p.textContent = m.text;
      bubble.appendChild(p);
    }

    const meta = document.createElement('div');
    meta.className = 'mt-1 flex items-center justify-end gap-2 text-[11px] text-gray-500';
    const time = document.createElement('span');
    const d = new Date(m.created_at);
    time.textContent = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    meta.appendChild(time);

    if (isMine) {
      const st = document.createElement('span');
      st.className = 'chat-status';
      st.dataset.messageId = m.id;
      st.textContent = 'Delivered';
      meta.appendChild(st);
    }

    bubble.appendChild(meta);
    wrap.appendChild(bubble);
    return wrap;
  };

  const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
  const socketUrl = `${wsScheme}://${window.location.host}/ws/chats/${conversationId}/`;
  const socket = new WebSocket(socketUrl);

  socket.addEventListener('open', () => {
    scrollToBottom();
    showWarning('');
    socket.send(JSON.stringify({ type: 'mark_read' }));
  });

  socket.addEventListener('message', (ev) => {
    try {
      const data = JSON.parse(ev.data);
      if (data.type === 'message') {
        const el = renderMessage(data.message);
        messagesEl.appendChild(el);
        scrollToBottom();
        if (Number(data.message.sender_id) !== currentUserId) {
          socket.send(JSON.stringify({ type: 'mark_read' }));
        }
      }
      if (data.type === 'send_result' && data.ok === false) {
        showWarning(data.error || 'Message blocked.');
      }
      if (data.type === 'read' && Number(data.user_id) !== currentUserId) {
        document.querySelectorAll('.chat-status').forEach((el) => {
          el.textContent = 'Read';
        });
      }
    } catch {
      // ignore
    }
  });

  socket.addEventListener('close', () => {
    showWarning('Realtime connection closed. Refresh the page.');
  });

  formEl?.addEventListener('submit', (e) => {
    e.preventDefault();
    const text = (inputEl.value || '').trim();
    if (!text) return;
    showWarning('');
    socket.send(JSON.stringify({ type: 'send_message', text }));
    inputEl.value = '';
  });

  imageFormEl?.addEventListener('submit', async (e) => {
    e.preventDefault();
    showWarning('');
    const formData = new FormData(imageFormEl);
    try {
      const res = await fetch(imageFormEl.action, {
        method: 'POST',
        body: formData,
        credentials: 'same-origin',
      });
      const json = await res.json();
      if (!json.ok) {
        showWarning(json.error || 'Image upload failed.');
      }
    } catch {
      showWarning('Image upload failed.');
    }
  });

  scrollToBottom();
})();
