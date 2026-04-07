// Simple pub/sub event bus
const EventBus = {
    events: {},

    subscribe(eventType, callback) {
        if (!this.events[eventType]) {
            this.events[eventType] = [];
        }
        this.events[eventType].push(callback);
    },

    publish(eventType, data) {
        if (this.events[eventType]) {
            this.events[eventType].forEach(cb => cb(data));
        }
    }
};

export default EventBus;
