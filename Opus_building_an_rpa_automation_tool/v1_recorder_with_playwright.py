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