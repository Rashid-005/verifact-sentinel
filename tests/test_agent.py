import unittest
from backend.agent import VeriFactSentinelAgent
from backend.nebius_client import NebiusNemotronClient
from backend.tavily_client import TavilyGroundingClient

class TestVeriFactSentinelAgent(unittest.TestCase):

    def setUp(self):
        self.agent = VeriFactSentinelAgent()

    def test_tavily_client_init(self):
        client = TavilyGroundingClient()
        self.assertIsNotNone(client)
        # Search should return valid dict structure
        res = client.search("NVIDIA Nemotron", max_results=1)
        self.assertIn("results", res)
        self.assertIn("query", res)

    def test_nebius_client_offline_synthesis(self):
        client = NebiusNemotronClient(api_key=None)
        self.assertFalse(client.is_live)
        
        # Test query planner prompt
        planner_prompt = [
            {"role": "system", "content": "You are the Lead Research Strategist for VeriFact Sentinel. Return ONLY a valid JSON array of 3 strings."},
            {"role": "user", "content": "Deconstruct this investigation target: LangChain"}
        ]
        out = client.chat_completion(planner_prompt)
        self.assertTrue(out.startswith("["))
        self.assertTrue(out.endswith("]"))

    def test_agent_investigation_stream(self):
        events = list(self.agent.run_investigation_stream("vLLM production inference engine"))
        self.assertGreater(len(events), 4)

        # Check final result payload
        final_event = events[-1]
        self.assertIn("result", final_event)
        result = final_event["result"]
        
        self.assertIn("topic", result)
        self.assertIn("dossier_markdown", result)
        self.assertIn("risk_data", result)
        self.assertIn("sources", result)
        self.assertGreaterEqual(result["risk_data"]["risk_score"], 0)
        self.assertLessEqual(result["risk_data"]["risk_score"], 100)

if __name__ == "__main__":
    unittest.main()
