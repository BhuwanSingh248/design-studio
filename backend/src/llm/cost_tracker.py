class CostTracker:
    def __init__(self, pricing:dict):
        self.pricing = pricing
        self.usage_data = {}

    def calculate_cost(self, model_name:str, tokens_input:int, tokens_output:int):
        if model_name not in self.pricing:
            raise ValueError(f"Unknown model: {model_name}")

        pricing = self.pricing[model_name]
        cost = (tokens_input * pricing['input']) + (tokens_output * pricing['output'])
        return cost
        
        

    def record_usage(self, user_id:str, tokens_input:int, tokens_output:int, cost:float):
        if user_id not in self.usage_data:
            self.usage_data[user_id] = {'input':0, 'output':0, 'cost':0.0}
        
        self.usage_data[user_id]['input'] += tokens_input
        self.usage_data[user_id]['output'] += tokens_output
        self.usage_data[user_id]['cost'] += cost

    def get_session_total(self, user_id):
        return self.usage_data.get(user_id, {'input':0, 'output':0, 'cost':0.0})

    