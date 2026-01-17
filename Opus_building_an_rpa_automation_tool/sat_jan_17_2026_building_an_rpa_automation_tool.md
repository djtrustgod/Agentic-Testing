# Copilot Chat Conversation Export: Building an RPA automation tool

**User:** @djtrustgod
**Thread URL:** https://github.com/copilot/c/813ba2fd-818e-42be-be0f-d15476460521

## @djtrustgod

How would you build an RPA automation tool that records a user's actions in the browser, and then plays them back?

## Copilot

Great question! Building an RPA (Robotic Process Automation) tool that records and plays back browser actions is a fascinating project.  Here's a comprehensive guide on how you could approach this:

## Architecture Overview

An RPA browser automation tool typically consists of three main components:

1. **Recorder** - Captures user interactions
2. **Storage** - Saves the recorded actions
3. **Player** - Replays the recorded actions

---

## 1. Recording User Actions

### Option A: Browser Extension Approach

The most common approach is building a browser extension that listens to DOM events:

```javascript name=content-script.js
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
```

### Option B: Proxy/Instrumentation Approach

For more control, you can use browser automation frameworks: 

```python name=recorder_with_playwright.py
from playwright.sync_api import sync_playwright
import json

class PlaywrightRecorder:
    def __init__(self):
        self.actions = []
    
    def start_recording(self, url):
        with sync_playwright() as p:
            browser = p.chromium. launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            # Inject recording script
            page.add_init_script("""
                window.__recordedActions = [];
                
                document.addEventListener('click', (e) => {
                    window.__recordedActions.push({
                        type: 'click',
                        selector: e.target.closest('[data-testid]')?.dataset.testid 
                                  || e.target.id 
                                  || e.target.tagName,
                        timestamp: Date.now()
                    });
                }, true);
                
                document. addEventListener('input', (e) => {
                    window.__recordedActions.push({
                        type: 'input',
                        selector: e.target.id || e.target.name,
                        value: e. target.value,
                        timestamp: Date.now()
                    });
                }, true);
            """)
            
            page. goto(url)
            
            input("Press Enter when done recording...")
            
            # Retrieve recorded actions
            self.actions = page.evaluate("window.__recordedActions")
            browser.close()
            
        return self.actions
    
    def save(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.actions, f, indent=2)
```

---

## 2. Storing Recorded Actions

Store actions in a structured format (JSON or YAML):

```json name=recorded_workflow.json
{
  "name": "Login and Submit Form",
  "createdAt": "2026-01-17T10:00:00Z",
  "startUrl": "https://example.com/login",
  "actions": [
    {
      "type": "navigate",
      "url": "https://example.com/login",
      "timestamp": 1737100000000
    },
    {
      "type": "input",
      "selector": "#username",
      "value": "testuser",
      "timestamp": 1737100001500
    },
    {
      "type": "input",
      "selector": "#password",
      "value": "{{PASSWORD}}",
      "timestamp": 1737100003000
    },
    {
      "type": "click",
      "selector": "button[type='submit']",
      "timestamp":  1737100004500
    },
    {
      "type":  "wait",
      "condition": "navigation",
      "timeout": 5000
    }
  ]
}
```

---

## 3. Playing Back Actions

```python name=player.py
from playwright.sync_api import sync_playwright
import json
import time

class WorkflowPlayer:
    def __init__(self, workflow_file):
        with open(workflow_file) as f:
            self.workflow = json.load(f)
    
    def play(self, variables=None):
        """
        Play back recorded actions. 
        variables: dict of template variables like {"PASSWORD": "secret123"}
        """
        variables = variables or {}
        
        with sync_playwright() as p:
            browser = p.chromium. launch(headless=False)
            page = browser.new_page()
            
            for action in self.workflow['actions']: 
                self._execute_action(page, action, variables)
            
            browser.close()
    
    def _execute_action(self, page, action, variables):
        action_type = action['type']
        
        if action_type == 'navigate':
            page. goto(action['url'])
            
        elif action_type == 'click':
            page.wait_for_selector(action['selector'], timeout=10000)
            page.click(action['selector'])
            
        elif action_type == 'input':
            value = action['value']
            # Replace template variables like {{PASSWORD}}
            for key, val in variables.items():
                value = value.replace(f'{{{{{key}}}}}', val)
            
            page.wait_for_selector(action['selector'], timeout=10000)
            page.fill(action['selector'], value)
            
        elif action_type == 'wait': 
            if action. get('condition') == 'navigation':
                page. wait_for_load_state('networkidle')
            elif action.get('selector'):
                page.wait_for_selector(action['selector'])
            else:
                time.sleep(action.get('duration', 1000) / 1000)
                
        elif action_type == 'screenshot':
            page.screenshot(path=action. get('path', 'screenshot.png'))

# Usage
player = WorkflowPlayer('recorded_workflow.json')
player.play(variables={'PASSWORD': 'my_secure_password'})
```

---

## 4. Key Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| **Fragile selectors** | Use multiple selector strategies (ID → data-testid → aria-label → CSS path) |
| **Dynamic content/timing** | Add smart waits (wait for element, network idle, animations) |
| **iframes** | Switch context to iframe before interacting |
| **Shadow DOM** | Use `>>>` piercing selectors or evaluate JS directly |
| **Authentication** | Store session cookies or use credential vaults |
| **Captchas** | Pause for human intervention or integrate captcha services |

---

## 5. Popular Open-Source Tools for Reference

- **[Playwright](https://playwright.dev/)** - Microsoft's automation library with codegen feature
- **[Puppeteer](https://pptr.dev/)** - Chrome automation from Google
- **[Selenium IDE](https://www.selenium.dev/selenium-ide/)** - Record & playback browser extension
- **[Katalon Recorder](https://katalon.com/)** - Free Chrome extension for recording
- **[Automa](https://github.com/AutomaApp/automa)** - Open-source browser automation extension

---

## Quick Start Recommendation

If you want to prototype quickly, **Playwright's codegen** feature does exactly this:

```bash
# Install Playwright
pip install playwright
playwright install

# Start recording - opens a browser and records your actions as code! 
playwright codegen https://example.com --output recorded_test.py
```

This generates Python/JavaScript code for everything you do in the browser, which you can then customize and replay.

Would you like me to dive deeper into any specific aspect—like building the browser extension, handling edge cases, or setting up a full project structure? 

## @djtrustgod

Save this as MD file in the repo as RPA-Options-From-Opus.md
