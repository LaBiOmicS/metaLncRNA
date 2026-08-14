import sys
import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import io

class TestLncRNAAgent(unittest.TestCase):
    def setUp(self):
        # Create a dummy results dataframe
        data = {
            "sequence_id": ["transcript_01", "transcript_02"],
            "consensus_label": ["noncoding", "coding"],
            "meta_score": [0.2, 0.8],
            "consensus_support": ["7/7", "6/7"],
            "consensus_support_count": [7, 6],
            "rnasamba_prob": [0.1, 0.9],
            "cpat_prob": [0.2, 0.7]
        }
        self.df = pd.DataFrame(data)

    def test_summarize_results(self):
        mock_ollama = MagicMock()
        mock_ollama.generate.return_value = {'response': "This is a summary."}
        with patch.dict(sys.modules, {'ollama': mock_ollama}):
            from metalncrna.utils.agent import LncRNAAgent
            agent = LncRNAAgent(model="llama3.2")
            summary = agent.summarize_results(self.df)
            self.assertEqual(summary, "This is a summary.")

    def test_explain_sequence(self):
        mock_ollama = MagicMock()
        mock_ollama.generate.return_value = {'response': "Explanation for sequence."}
        with patch.dict(sys.modules, {'ollama': mock_ollama}):
            from metalncrna.utils.agent import LncRNAAgent
            agent = LncRNAAgent(model="llama3.2")
            explanation = agent.explain_sequence("transcript_01", self.df)
            self.assertEqual(explanation, "Explanation for sequence.")

    def test_explain_sequence_not_found(self):
        mock_ollama = MagicMock()
        with patch.dict(sys.modules, {'ollama': mock_ollama}):
            from metalncrna.utils.agent import LncRNAAgent
            agent = LncRNAAgent(model="llama3.2")
            explanation = agent.explain_sequence("unknown", self.df)
            self.assertIn("not found", explanation)

if __name__ == '__main__':
    unittest.main()
