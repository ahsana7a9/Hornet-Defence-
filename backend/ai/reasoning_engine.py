import ollama
import json
import logging

logger = logging.getLogger(__name__)

class ReasoningEngine:
    """
    The LLM Reasoning Cortex for Hornet-Defence.
    Uses Ollama (Llama3) to analyze complex network states.
    """
    def __init__(self, model_name="llama3"):
        self.model_name = model_name

    def analyze_threat(self, agent_name, state_data):
        """
        Sends network state to LLM and gets a structured decision.
        """
        # Create a concise prompt for the LLM
        prompt = f"""
        Role: Swarm Security Intelligence
        Agent: {agent_name}
        Context: {json.dumps(state_data)}

        Task: Analyze if this activity is a threat. 
        Options: BLOCK, MONITOR, IGNORE.
        
        Respond ONLY in JSON:
        {{
            "decision": "ACTION",
            "reasoning": "Short explanation",
            "confidence": 0.0-1.0
        }}
        """

        try:
            # Call local Ollama instance
            response = ollama.generate(model=self.model_name, prompt=prompt)
            raw_text = response['response']
            
            # Extract JSON from the response
            start = raw_text.find("{")
            end = raw_text.rfind("}") + 1
            return json.loads(raw_text[start:end])

        except Exception as e:
            logger.warning(f"[AI] Ollama Reasoning failed (is it running?): {e}")
            # Fallback Logic: If AI fails, use the anomaly score
            score = state_data.get("anomaly_score", 0.0)
            decision = "BLOCK" if score >= 0.7 else "MONITOR"
            return {
                "decision": decision,
                "reasoning": "Fallback: AI Offline",
                "confidence": 0.5
            }
