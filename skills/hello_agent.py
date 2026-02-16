from dino_os.agent_core import Agent


class HelloAgent(Agent):
    """Example agent that says hello."""
    
    name = "hello"
    description = "Says hello from Dino Dynasty OS"
    
    async def run(self):
        """Run the hello agent."""
        print("Hello from Dino Dynasty OS!")
        return {"status": "success"}
