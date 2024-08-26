import torch
from sentence_transformers import SentenceTransformer, util

class TextSimilarityService:
    def __init__(self):
        model_path = r'C:\Users\Imad AHADAD\OneTrack\apps\home\transformers\SBERT_all-MiniLM-L6-v2'
        self.model = SentenceTransformer(model_path)
        print("Model loaded")

    def find_similar_descriptions(self, user_input, vulnerabilities):
        # Extract vulnerability descriptions
        vuln_descriptions = [vuln.vuln_description for vuln in vulnerabilities]

        # Encode the descriptions and user input using SBERT
        encoded_descriptions = self.model.encode(vuln_descriptions, convert_to_tensor=True)
        encoded_input = self.model.encode(user_input, convert_to_tensor=True)

        # Compute cosine similarities
        cosine_scores = util.pytorch_cos_sim(encoded_input, encoded_descriptions)

        # Get the top 5 most similar descriptions
        top_results = torch.topk(cosine_scores, k=5)

        # Convert the indices tensor to a list of integers
        top_indices = top_results[1].tolist()[0]  # Extract the indices from the tensor

        # Return the top similar vulnerabilities and their scores
        return [(vulnerabilities[idx], cosine_scores[0][idx].item()) for idx in top_indices]






