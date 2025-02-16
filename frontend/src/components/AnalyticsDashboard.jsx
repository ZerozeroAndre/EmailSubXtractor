import React from 'react';
import { Bar, Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import './AnalyticsDashboard.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const AnalyticsDashboard = ({ analytics }) => {
  if (!analytics) return null;

  const { 
    total_emails, 
    successful_extractions, 
    failed_extractions,
    category_distribution,
    service_analytics 
  } = analytics;

  // Prepare data for category distribution chart
  const categoryChartData = {
    labels: Object.keys(category_distribution || {}),
    datasets: [{
      data: Object.values(category_distribution || {}),
      backgroundColor: [
        '#FF6384',
        '#36A2EB',
        '#FFCE56',
        '#4BC0C0',
        '#9966FF',
        '#FF9F40'
      ]
    }]
  };

  // Prepare data for service amounts chart
  const serviceNames = Object.keys(service_analytics || {});
  const averageAmounts = serviceNames.map(name => service_analytics[name].average_amount);

  const serviceChartData = {
    labels: serviceNames,
    datasets: [{
      label: 'Average Subscription Amount ($)',
      data: averageAmounts,
      backgroundColor: '#36A2EB'
    }]
  };

  const barOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { 
        display: true,
        text: 'Average Subscription Amounts by Service'
      }
    }
  };

  return (
    <div className="analytics-dashboard" role="region" aria-labelledby="analytics-heading">
      <h2 id="analytics-heading">Analytics Dashboard</h2>
      
      <div className="stats-summary">
        <div className="stat-box">
          <h3>Total Emails</h3>
          <p>{total_emails}</p>
        </div>
        <div className="stat-box">
          <h3>Successful Extractions</h3>
          <p>{successful_extractions}</p>
        </div>
        <div className="stat-box">
          <h3>Failed Extractions</h3>
          <p>{failed_extractions}</p>
        </div>
      </div>

      <div className="charts-container">
        <div className="chart-box">
          <h3>Category Distribution</h3>
          <Pie data={categoryChartData} />
        </div>
        
        <div className="chart-box">
          <h3>Average Subscription Amounts</h3>
          <Bar options={barOptions} data={serviceChartData} />
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;