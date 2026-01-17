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