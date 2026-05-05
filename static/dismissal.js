// Socket configuration
const socket = io({
    transports: ['websocket', 'polling'],
    reconnection: true,
    reconnectionAttempts: Infinity,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    timeout: 20000,
    autoConnect: true
});

// Speech synthesis setup with permission handling
const speechQueue = [];
let isSpeaking = false;
let voices = [];
let hasPermission = false;

// Modified to auto-request permission
function autoRequestPermission() {
    try {
        // Create and trigger a silent utterance
        const test = new SpeechSynthesisUtterance('');
        test.volume = 0;
        test.onend = () => {
            hasPermission = true;
            console.log('Speech synthesis auto-enabled');
            // Process any queued announcements
            if (speechQueue.length > 0) {
                speakNext();
            }
        };
        test.onerror = () => {
            console.log('Auto-enable failed, falling back to button');
            addPermissionButton();
        };
        speechSynthesis.speak(test);
    } catch (error) {
        console.error('Auto-permission request failed:', error);
        addPermissionButton();
    }
}

// Initialize voices
function initVoices() {
    return new Promise((resolve) => {
        voices = speechSynthesis.getVoices();
        if (voices.length > 0) {
            resolve(voices);
        } else {
            speechSynthesis.onvoiceschanged = () => {
                voices = speechSynthesis.getVoices();
                resolve(voices);
            };
        }
    });
}

// Modified visibility handler - only log state changes
document.addEventListener('visibilitychange', () => {
    console.log('Visibility changed:', document.hidden ? 'hidden' : 'visible');
    // No longer cancel speech when hidden
});

// Handle page refresh/unload
window.addEventListener('beforeunload', () => {
    speechSynthesis.cancel();
});

function getPronunciation(name) {
    if (!name) return '';
    
    // Split by comma and handle parentheses
    const students = name.split(',').map(student => {
        // Extract name and year
        const match = student.trim().match(/(.*?)\s*(\([^)]*\))?$/);
        if (!match) return '';
        
        const [_, studentName, year] = match;
        
        // Process each word in the name
        const pronouncedName = studentName
            .trim()
            .split(' ')
            .map(word => pronunciationDict[word] || word)
            .join(' ');
            
        // Return name with year if present
        return year ? `${pronouncedName} ${year}` : pronouncedName;
    });
    
    // Join all processed names back together
    return students.join(', ');
}

function speakNext() {
    if (speechQueue.length === 0 || isSpeaking || !hasPermission) return;

    const text = speechQueue.shift();
    isSpeaking = true;

    try {
        // Split into students and lane
        const lastCommaIndex = text.lastIndexOf(',');
        const studentNames = text.substring(0, lastCommaIndex);
        const lane = text.substring(lastCommaIndex + 1);
        
        // Get pronunciation for all student names
        const pronouncedNames = getPronunciation(studentNames);
        console.log('Original:', studentNames, 'Pronounced:', pronouncedNames); // Debug log
        
        // Create the final announcement text
        const pronouncedText = `${pronouncedNames},${lane}`;

        const utterance = new SpeechSynthesisUtterance(pronouncedText);
        utterance.rate = 0.9;
        utterance.pitch = 1;
        
        // Use cached voices
        const englishVoice = voices.find(voice => 
            voice.lang.startsWith('en') && voice.name.includes('Female')
        );
        if (englishVoice) utterance.voice = englishVoice;

        utterance.onend = () => {
            isSpeaking = false;
            speakNext();
        };

        utterance.onerror = (error) => {
            console.error('Speech synthesis error:', error);
            isSpeaking = false;
            if (error.error === 'not-allowed' && hasPermission) {
                hasPermission = false;
                addPermissionButton();
            }
            setTimeout(() => speakNext(), 1000);
        };

        speechSynthesis.speak(utterance);
    } catch (error) {
        console.error('Speech synthesis error:', error);
        isSpeaking = false;
        speakNext();
    }
}

// Modified initialization
document.addEventListener('DOMContentLoaded', () => {
    initVoices().then(() => {
        console.log('Speech synthesis initialized with', voices.length, 'voices');
        // Try auto-enabling first
        autoRequestPermission();
    });
});

// Keep existing permission button as fallback
function addPermissionButton() {
    const button = document.createElement('button');
    button.textContent = 'Enable Announcements';
    button.style.cssText = `
        position: fixed;
        top: 10px;
        right: 10px;
        padding: 10px;
        background: #4CAF50;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        z-index: 1000;
    `;
    button.onclick = requestPermission;
    document.body.appendChild(button);
}

// Request permission through user interaction
async function requestPermission() {
    try {
        // Try a test utterance
        const test = new SpeechSynthesisUtterance('');
        speechSynthesis.speak(test);
        hasPermission = true;
        
        // Remove the permission button
        const button = document.querySelector('button');
        if (button) button.remove();
        
        // Process any queued announcements
        if (speechQueue.length > 0) {
            speakNext();
        }
    } catch (error) {
        console.error('Permission request failed:', error);
    }
}

function updateDisplay(data) {
    try {
        if (!data) return;
        
        // Update display elements
        if (data.studentname) {
            document.getElementById('studentname').innerHTML = `<div>${data.studentname}</div>`;
        }
        if (data.lane) {
            document.getElementById('lane').innerHTML = `<div>${data.lane}</div>`;
            // Queue announcement even if we don't have permission yet
            const announcement = `${data.studentname}, ${data.lane}`;
            speechQueue.push(announcement);
            if (hasPermission && !isSpeaking) {
                speakNext();
            }
        }
        if (data.recent_list) {
            document.getElementById('recent_list').innerHTML = `<h1>${data.recent_list}</h1>`;
        }
    } catch (error) {
        console.error('Error updating display:', error);
    }
}

// Socket event handlers
socket.on('update_data', data => updateDisplay(data));

socket.on('connect', () => {
    console.log('Connected to server');
    document.getElementById('connection-status').style.display = 'none';
});

socket.on('disconnect', () => {
    console.log('Disconnected from server');
    document.getElementById('connection-status').style.display = 'block';
});

// Connection error handling
socket.on('connect_error', (error) => {
    console.error('Connection error:', error);
    const statusEl = document.getElementById('connection-status');
    if (statusEl) {
        statusEl.style.display = 'block';
        statusEl.textContent = 'Connection lost. Attempting to reconnect...';
        statusEl.style.backgroundColor = '#ff4444';
        statusEl.style.color = 'white';
        statusEl.style.padding = '10px';
        statusEl.style.position = 'fixed';
        statusEl.style.top = '0';
        statusEl.style.width = '100%';
        statusEl.style.textAlign = 'center';
        statusEl.style.zIndex = '1000';
    }
});

// Keep-alive ping/pong
setInterval(() => socket.connected && socket.emit('ping'), 25000);
socket.on('pong', () => console.log('Received pong from server'));
