"""
Train AI Models Script
Trains all AI models with generated training data
"""

from training_data import generate_performance_training_data, generate_turnover_training_data
from performance.performance_predictor import performance_predictor
from forecasting.turnover_predictor import turnover_predictor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_all_models():
    """Train all AI models"""
    
    logger.info("="*60)
    logger.info("Starting AI Model Training")
    logger.info("="*60)
    
    # Train Performance Model
    logger.info("
1. Training Performance Prediction Model...")
    perf_data = generate_performance_training_data(1000)
    perf_results = performance_predictor.train(perf_data)
    logger.info(f"Performance Model Results: {perf_results}")
    
    # Save model
    performance_predictor.save_model('models/performance_v1.pkl')
    logger.info("Performance model saved to models/performance_v1.pkl")
    
    # Train Turnover Model
    logger.info("
2. Training Turnover Prediction Model...")
    turnover_data = generate_turnover_training_data(1000)
    turnover_results = turnover_predictor.train(turnover_data)
    logger.info(f"Turnover Model Results: {turnover_results}")
    
    # Save model
    turnover_predictor.save_model('models/turnover_v1.pkl')
    logger.info("Turnover model saved to models/turnover_v1.pkl")
    
    logger.info("
" + "="*60)
    logger.info("AI Model Training Complete!")
    logger.info("="*60)
    
    return {
        'performance': perf_results,
        'turnover': turnover_results
    }

if __name__ == '__main__':
    results = train_all_models()
    print("
Training Summary:")
    print(f"Performance Model - Train R²: {results['performance']['train_score']:.3f}")
    print(f"Performance Model - Test R²: {results['performance']['test_score']:.3f}")
    print(f"Turnover Model - Accuracy: {results['turnover']['accuracy']:.3f}")
