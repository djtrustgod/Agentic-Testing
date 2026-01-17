// Content script that runs on web pages
class ActionRecorder {
  constructor() {
    this.actions = [];
    this.isRecording = false;
  }

  start() {
    this.isRecording = true;
    this.attachListeners();
  }

  stop() {
    this.isRecording = false;
    this. detachListeners();
    return this.actions;
  }

  attachListeners() {
    // Click events
    document.addEventListener('click', this.handleClick.bind(this), true);
    
    // Input/typing events
    document.addEventListener('input', this.handleInput.bind(this), true);
    
    // Form submissions
    document.addEventListener('submit', this.handleSubmit.bind(this), true);
    
    // Keyboard events (for shortcuts, navigation)
    document.addEventListener('keydown', this.handleKeydown. bind(this), true);
    
    // Scroll events
    document.addEventListener('scroll', this. handleScroll.bind(this), true);
  }

  handleClick(event) {
    if (! this.isRecording) return;
    
    this.actions.push({
      type: 'click',
      timestamp: Date.now(),
      selector: this.generateSelector(event. target),
      coordinates: { x: event.clientX, y: event.clientY },
      url: window.location.href
    });
  }

  handleInput(event) {
    if (!this.isRecording) return;
    
    this.actions. push({
      type: 'input',
      timestamp: Date. now(),
      selector: this. generateSelector(event.target),
      value: event.target.value,
      url: window.location.href
    });
  }

  // Generate a robust CSS selector for an element
  generateSelector(element) {
    // Priority:  ID > data-testid > unique class > nth-child path
    if (element.id) {
      return `#${element.id}`;
    }
    
    if (element.dataset.testid) {
      return `[data-testid="${element.dataset.testid}"]`;
    }
    
    // Build a path using nth-child for robustness
    const path = [];
    while (element && element.nodeType === Node.ELEMENT_NODE) {
      let selector = element.tagName.toLowerCase();
      
      if (element.id) {
        selector = `#${element.id}`;
        path.unshift(selector);
        break;
      }
      
      const siblings = element.parentNode?. children || [];
      const index = Array.from(siblings).indexOf(element) + 1;
      selector += `:nth-child(${index})`;
      
      path.unshift(selector);
      element = element.parentNode;
    }
    
    return path.join(' > ');
  }
}