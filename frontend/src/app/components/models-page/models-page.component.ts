import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-models-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './models-page.component.html',
  styleUrl: './models-page.component.scss'
})
export class ModelsPageComponent {
  model = {
    name: 'FraudShield RF-v1',
    algorithm: 'Random Forest Classifier',
    version: '1.0.0',
    status: 'Deployed',
    trainedOn: 'Credit Card Fraud Detection Dataset (Kaggle) (284,807 transactions)',
    predictionLatency: '< 50 ms',
    lastTrainingDate: '02 Jul 2026',
    estimators: 200,
    maxDepth: 12,
    balancing: 'SMOTE oversampling',
    metrics: [
      { label: 'Accuracy', value: '99.94%', desc: 'Overall proportion of correct predictions.' },
      { label: 'Precision', value: '88.2%', desc: 'Of flagged transactions, how many were truly fraud.' },
      { label: 'Recall', value: '82.7%', desc: 'Of all fraud cases, how many were correctly caught.' },
      { label: 'F1 Score', value: '85.4%', desc: 'Balance between Precision and Recall.' },
      { label: 'ROC-AUC', value: '0.976', desc: 'Ability to distinguish fraud from normal cases.' },
      { label: 'PR-AUC', value: '0.854', desc: 'Precision-Recall trade-off on rare fraud cases.' },
    ],
    topFeatures: [
      { name: 'V14', importance: 18 },
      { name: 'V4', importance: 14 },
      { name: 'V12', importance: 11 },
      { name: 'V10', importance: 9 },
      { name: 'V17', importance: 8 },
    ]
  };

  modelComparison = [
    { model: 'Logistic Regression', status: 'Evaluated', comment: 'Good baseline but lower fraud detection performance', selected: false },
    { model: 'Decision Tree', status: 'Evaluated', comment: 'Simple but prone to overfitting', selected: false },
    { model: 'Random Forest', status: 'Selected', comment: 'Best overall balance between precision, recall and robustness', selected: true },
  ];

  trainingPipeline = [
    'Historical Transaction Dataset',
    'Data Cleaning & Preprocessing',
    'SMOTE Oversampling',
    'Train / Test Split',
    'Random Forest Training',
    'Model Evaluation',
    'Model Deployment',
  ];

  detectionWorkflow = [
    'Incoming Transaction',
    'Feature Extraction',
    'Random Forest Prediction',
    'Fraud Probability',
    'Decision Threshold',
  ];

  whyReasons = [
    { title: 'Better Precision & Recall', description: 'Balances fraud detection and false positives.', color: 'pink' },
    { title: 'Robust Ensemble', description: 'More stable than a single Decision Tree.', color: 'blue' },
    { title: 'Reduced Overfitting', description: 'Improves generalization on unseen data.', color: 'green' },
    { title: 'Feature Importance', description: 'Provides interpretable feature rankings.', color: 'yellow' },
    { title: 'SMOTE Compatibility', description: 'Performs well on highly imbalanced datasets.', color: 'purple' },
    { title: 'Easy to Maintain', description: 'Well suited for production and academic projects.', color: 'orange' },
  ];
}
