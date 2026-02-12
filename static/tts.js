/**
 * ParentEye Text-to-Speech Module
 * Enables voice output for dashboard notifications and data
 */

class TextToSpeech {
    constructor() {
        this.isEnabled = localStorage.getItem('ttsEnabled') === 'true';
        this.voices = [];
        this.isSpeaking = false;
        this.currentUtterance = null;
        this.rate = parseFloat(localStorage.getItem('ttsRate')) || 1.0;
        this.volume = parseFloat(localStorage.getItem('ttsVolume')) || 1.0;
        
        // Initialize on page load
        if ('speechSynthesis' in window) {
            this.initVoices();
        }
    }

    /**
     * Initialize available voices
     */
    initVoices() {
        this.voices = window.speechSynthesis.getVoices();
        if (this.voices.length === 0) {
            window.speechSynthesis.onvoiceschanged = () => {
                this.voices = window.speechSynthesis.getVoices();
            };
        }
    }

    /**
     * Speak text
     * @param {string} text - Text to speak
     * @param {object} options - Speech options (pitch, rate, etc.)
     */
    speak(text, options = {}) {
        if (!this.isEnabled || !('speechSynthesis' in window)) {
            return;
        }

        // Cancel any previous utterance
        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        
        // Set properties
        utterance.rate = options.rate || this.rate;
        utterance.pitch = options.pitch || 1.0;
        utterance.volume = options.volume || this.volume;

        // Set voice if specified
        if (options.voiceName && this.voices.length > 0) {
            const voice = this.voices.find(v => v.name === options.voiceName);
            if (voice) utterance.voice = voice;
        } else if (this.voices.length > 0) {
            // Use first available voice
            utterance.voice = this.voices[0];
        }

        // Event handlers
        utterance.onstart = () => {
            this.isSpeaking = true;
            this.onSpeakStart();
        };

        utterance.onend = () => {
            this.isSpeaking = false;
            this.onSpeakEnd();
        };

        utterance.onerror = (event) => {
            this.isSpeaking = false;
            console.error('Speech synthesis error:', event);
            this.onSpeakError(event);
        };

        this.currentUtterance = utterance;
        window.speechSynthesis.speak(utterance);
    }

    /**
     * Announce notification message
     * @param {string} message - Notification message
     * @param {string} type - Type: 'info', 'success', 'warning', 'error'
     */
    announceNotification(message, type = 'info') {
        if (!this.isEnabled) return;

        const typePrefix = {
            'info': 'Information:',
            'success': 'Success:',
            'warning': 'Warning:',
            'error': 'Error:',
        };

        const fullMessage = `${typePrefix[type]} ${message}`;
        this.speak(fullMessage, { rate: 0.9 });
    }

    /**
     * Announce device status
     * @param {string} deviceName - Device name
     * @param {string} status - Status: 'online', 'offline'
     */
    announceDeviceStatus(deviceName, status) {
        if (!this.isEnabled) return;

        const message = status === 'online' 
            ? `Device ${deviceName} is now online`
            : `Device ${deviceName} has gone offline`;
        
        this.speak(message);
    }

    /**
     * Announce monitoring data
     * @param {string} dataType - Type: 'keystroke', 'location', 'screenshot', etc.
     * @param {string} detail - Data detail
     */
    announceData(dataType, detail) {
        if (!this.isEnabled) return;

        const prefix = {
            'keystroke': 'New keystroke data received:',
            'location': 'Location updated:',
            'screenshot': 'Screenshot captured',
            'webcam': 'Webcam image captured',
            'website': 'Website blocked:',
            'command': 'Command executed:'
        };

        const fullMessage = detail 
            ? `${prefix[dataType]} ${detail}`
            : prefix[dataType] || `Data received: ${dataType}`;
        
        this.speak(fullMessage, { rate: 0.95 });
    }

    /**
     * Stop speaking
     */
    stop() {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
            this.isSpeaking = false;
        }
    }

    /**
     * Toggle TTS on/off
     */
    toggle() {
        this.isEnabled = !this.isEnabled;
        localStorage.setItem('ttsEnabled', this.isEnabled);
        return this.isEnabled;
    }

    /**
     * Set speech rate (0.5 to 2.0)
     * @param {number} rate - Speech rate
     */
    setRate(rate) {
        this.rate = Math.max(0.5, Math.min(2.0, rate));
        localStorage.setItem('ttsRate', this.rate);
    }

    /**
     * Set volume (0 to 1)
     * @param {number} volume - Volume level
     */
    setVolume(volume) {
        this.volume = Math.max(0, Math.min(1, volume));
        localStorage.setItem('ttsVolume', this.volume);
    }

    /**
     * Get available voices
     * @returns {array} Voice objects
     */
    getVoices() {
        return this.voices;
    }

    /**
     * Set voice by name
     * @param {string} voiceName - Voice name
     */
    setVoice(voiceName) {
        localStorage.setItem('ttsVoice', voiceName);
    }

    /**
     * Test TTS with sample message
     */
    test() {
        this.speak('Text to speech is now enabled. You will hear voice notifications for all dashboard events.');
    }

    // Event callbacks (can be overridden)
    onSpeakStart() {
        console.log('Speech started');
    }

    onSpeakEnd() {
        console.log('Speech ended');
    }

    onSpeakError(event) {
        console.error('Speech error:', event.error);
    }
}

// Create global TTS instance
const tts = new TextToSpeech();

/**
 * Helper function for quick announcements
 */
function announceMessage(message, type = 'info') {
    tts.announceNotification(message, type);
}

/**
 * Helper function to announce device updates
 */
function announceDeviceUpdate(deviceName, status) {
    tts.announceDeviceStatus(deviceName, status);
}

/**
 * Helper function to announce data updates
 */
function announceUpdate(dataType, detail) {
    tts.announceData(dataType, detail);
}
