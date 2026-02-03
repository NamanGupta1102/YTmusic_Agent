const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const messagesContainer = document.getElementById('messages-container');
const cartList = document.getElementById('cart-list');
const cartCount = document.getElementById('cart-count');
const loadingOverlay = document.getElementById('loading-overlay');

// Auth Modal
const authBtn = document.getElementById('auth-btn');
const authModal = document.getElementById('auth-modal');
const closeBtn = document.querySelector('.close-btn');
const saveAuthBtn = document.getElementById('save-auth-btn');
const curlInput = document.getElementById('curl-input');

// --- EVENT LISTENERS ---

document.addEventListener('DOMContentLoaded', () => {
    fetchCart();
});

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = userInput.value.trim();
    if (!message) return;

    addMessage(message, 'user');
    userInput.value = '';

    await sendMessageToAgent(message);
});

// Auth Modal Logic
authBtn.onclick = () => authModal.classList.add('visible');
closeBtn.onclick = () => authModal.classList.remove('visible');
window.onclick = (event) => {
    if (event.target == authModal) {
        authModal.classList.remove('visible');
    }
};

saveAuthBtn.onclick = async () => {
    const curl = curlInput.value.trim();
    if (!curl) return alert("Please paste a curl command");

    loadingOverlay.classList.remove('hidden');
    try {
        const res = await fetch('/api/auth', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ curl_command: curl })
        });
        const data = await res.json();
        if (res.ok) {
            alert("Success! " + data.message);
            authModal.classList.remove('visible');
            curlInput.value = '';
        } else {
            alert("Error: " + data.detail);
        }
    } catch (err) {
        console.error(err);
        alert("Failed to connect to server");
    } finally {
        loadingOverlay.classList.add('hidden');
    }
}

// --- FUNCTIONS ---

function addMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender);

    const bubble = document.createElement('div');
    bubble.classList.add('bubble');
    bubble.textContent = text;

    msgDiv.appendChild(bubble);
    messagesContainer.appendChild(msgDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

async function sendMessageToAgent(message) {
    loadingOverlay.classList.remove('hidden');
    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });
        const data = await res.json();

        if (res.ok) {
            addMessage(data.agent_response, 'agent');
            updateCartUI(data.cart);
        } else {
            addMessage(`Error: ${data.detail}`, 'agent');
        }
    } catch (error) {
        console.error(error);
        addMessage("Error: Failed to reach the server. Is it running?", 'agent');
    } finally {
        loadingOverlay.classList.add('hidden');
    }
}

async function fetchCart() {
    try {
        const res = await fetch('/api/cart');
        const data = await res.json();
        if (data.cart) {
            updateCartUI(data.cart);
        }
    } catch (err) {
        console.error("Failed to fetch cart", err);
    }
}

function updateCartUI(cart) {
    cartList.innerHTML = '';
    cartCount.textContent = `${cart.length} songs`;

    if (cart.length === 0) {
        cartList.innerHTML = '<div class="empty-state">Cart is empty</div>';
        return;
    }

    cart.forEach(item => {
        const div = document.createElement('div');
        div.classList.add('cart-item');

        let thumb = "https://via.placeholder.com/40";
        if (item.thumbnails && item.thumbnails.length > 0) {
            thumb = item.thumbnails[0].url;
        }

        div.innerHTML = `
            <img src="${thumb}" alt="Art">
            <div class="cart-item-info">
                <div class="cart-item-title" title="${item.title}">${item.title}</div>
                <div class="cart-item-artist">${item.artist || 'Unknown'}</div>
            </div>
        `;
        cartList.appendChild(div);
    });
}
