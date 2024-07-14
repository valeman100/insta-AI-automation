prices = {
    'gpt-4o-2024-05-13': {'prompt_cost': 5/1e6, 'completion_cost': 15/1e6},
    'gpt-3.5-turbo': {'prompt_cost': 0.5/1e6, 'completion_cost': 1.5/1e6},
    'gpt-3.5-turbo-0125': {'prompt_cost': 0.5/1e6, 'completion_cost': 1.5/1e6},
    'gpt-4-turbo': {'prompt_cost': 10/1e6, 'completion_cost': 30/1e6}}


class OpenaiResponse:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if isinstance(value, dict):
                # Recursively create an instance of GenericClass for nested dictionaries
                setattr(self, key, OpenaiResponse(**value))
            else:
                setattr(self, key, value)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__})"


def calculate_cost(completion):
    if isinstance(completion, dict):
        completion = OpenaiResponse(**completion)
    call_cost = 0.

    call_cost += (prices[completion.model]['prompt_cost'] * completion.usage.prompt_tokens +
                  prices[completion.model]['completion_cost'] * completion.usage.completion_tokens)

    return round(call_cost, 7)
