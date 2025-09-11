import argparse
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer


class Similarity():
    def __init__(self):
        self.sentences = ["Cosine similarity measures the angle between two vectors to determine their similarity",
                    "The cosine similarity metric evaluates how close two vectors are by calculating the cosine of the angle between them",
                    "Machine learning models require large datasets to achieve high accuracy"
                ]
        self.output_dir = '.'
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
    def calculate(self, sentences=None, output_dir=None):
        # If None use default values
        if sentences is None:
            sentences = self.sentences
        if output_dir is None:
            output_dir = self.output_dir
            
        # Read input data and prepare output dir
        if isinstance(sentences, str): 
            if not sentences.endswith('.txt'):
                raise NameError(f'File {sentences} should be txt file.')
            with open(sentences, 'r') as file:
                sentences = file.readlines()
                if len(sentences) > 3:
                  raise ValueError(f'You should use only 3 sentences.')
        os.makedirs(output_dir, exist_ok=True)

        # Model forward
        embeddings = self.model.encode(sentences)
        cosine_sim_matrix = cosine_similarity(embeddings)
        
        # Save results
        plt.figure(figsize=(8, 6))
        sns.heatmap(
            cosine_sim_matrix,
            annot=True,
            cmap="YlGnBu",
            xticklabels=["Sentence 1", "Sentence 2", "Sentence 3"],
            yticklabels=["Sentence 1", "Sentence 2", "Sentence 3"],
            vmin=-1, vmax=1
        )

        plt.title("Cosine Similarity Matrix for Sentence Embeddings")
        plt.savefig(os.path.join(output_dir, "sim_matrix.jpg"))


parser = argparse.ArgumentParser(description='Encode sentences.')
parser.add_argument('-s', '--sentences', type=str, default=None, help='Path to txt file with input sentences.')
parser.add_argument('-o', '--output_dir', type=str, default=None, help='Path for saving output.')
args = parser.parse_args()

cos_sim = Similarity()
cos_sim.calculate(sentences=args.sentences, output_dir=args.output_dir)