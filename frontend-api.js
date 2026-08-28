(() => {
  const apiBase = window.ECOSORT_API_URL || 'http://127.0.0.1:5000/api';
  let chatSessionId = null;
  let apiAvailable = false;

  async function request(path, options = {}) {
    const response = await fetch(`${apiBase}${path}`, { headers: { 'Content-Type': 'application/json', ...(options.headers || {}) }, ...options });
    if (!response.ok) throw new Error(`API request failed: ${response.status}`);
    return response.json();
  }

  function addMessage(className, text) {
    const messages = document.querySelector('#chat-messages');
    if (!messages) return;
    const message = document.createElement('div');
    message.className = className;
    message.textContent = text;
    messages.appendChild(message);
    messages.scrollTop = messages.scrollHeight;
  }

  async function startChat() {
    if (chatSessionId) return;
    try {
      const result = await request('/chat/start', { method: 'POST' });
      chatSessionId = result.sessionId;
      apiAvailable = true;
      const messages = document.querySelector('#chat-messages');
      if (messages) messages.innerHTML = '';
      addMessage('bot-message', result.message);
    } catch (error) {
      apiAvailable = false;
      console.warn('EcoSort chat backend unavailable:', error.message);
    }
  }

  async function sendChat(message) {
    await startChat();
    if (!apiAvailable || !chatSessionId) return false;
    addMessage('user-message', message);
    const result = await request('/chat/message', { method: 'POST', body: JSON.stringify({ sessionId: chatSessionId, message }) });
    addMessage('bot-message', result.reply);
    return true;
  }

  document.addEventListener('click', async (event) => {
    if (event.target.closest('#chat-toggle')) await startChat();
    const sendButton = event.target.closest('#chat-send');
    if (!sendButton) return;
    event.stopImmediatePropagation();
    const input = document.querySelector('#chat-input');
    const message = input?.value.trim();
    if (!message) return;
    try {
      if (await sendChat(message)) input.value = '';
    } catch (error) {
      console.warn('EcoSort chat request failed:', error.message);
      apiAvailable = false;
    }
  }, true);

  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Enter' || event.target.id !== 'chat-input') return;
    event.preventDefault();
    event.stopImmediatePropagation();
    document.querySelector('#chat-send')?.click();
  }, true);

  document.addEventListener('submit', (event) => {
    if (event.target.id !== 'login-form') return;
    const state = JSON.parse(localStorage.getItem('ecosort-state') || 'null');
    if (!state?.registration) return;
    request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        userType: state.persona === 'public' ? 'RESIDENT' : 'STUDENT',
        username: state.name,
        registrationNumber: state.persona === 'student' ? state.registration : undefined,
        employeeId: state.persona === 'public' ? state.registration : undefined,
        collegeName: state.place,
        hostel: state.unit,
        roomNumber: state.space,
        department: state.department,
        year: state.year,
        area: state.area,
      }),
    }).catch((error) => console.warn('EcoSort profile backend unavailable:', error.message));
  }, true);
})();
