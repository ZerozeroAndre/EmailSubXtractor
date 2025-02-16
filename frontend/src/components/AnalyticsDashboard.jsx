// src/components/AnalyticsDashboard.jsx
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
    service_analytics,
    duplicate_subscriptions_details,
    deduplicated_subscriptions
  } = analytics;

  // Prepare data for category distribution chart.
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

  // Prepare data for service amounts chart.
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

  // Prepare data for duplicate subscriptions chart.
  const duplicateLabels = Object.keys(duplicate_subscriptions_details || {});
  const duplicateCounts = duplicateLabels.map(label => duplicate_subscriptions_details[label].count);

  const duplicateChartData = {
    labels: duplicateLabels,
    datasets: [{
      label: 'Duplicate Count',
      data: duplicateCounts,
      backgroundColor: '#FF6384'
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

  const duplicateBarOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { 
        display: true,
        text: 'Duplicate Subscriptions'
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

        <div className="chart-box">
          <h3>Duplicate Subscriptions</h3>
          {duplicateLabels.length > 0 ? (
            <Bar options={duplicateBarOptions} data={duplicateChartData} />
          ) : (
            <p>No duplicate subscriptions found.</p>
          )}
        </div>
      </div>

      {/* New Deduplicated Subscriptions Table */}
      <div className="deduped-subscriptions">
        <h3>Deduplicated Subscriptions</h3>
        {deduplicated_subscriptions && Object.keys(deduplicated_subscriptions).length > 0 ? (
          <table>
            <thead>
              <tr>
                <th>Subscription Name</th>
                <th>Count</th>
                <th>Category</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(deduplicated_subscriptions).map(([name, info]) => (
                <tr key={name}>
                  <td>{name}</td>
                  <td>{info.count}</td>
                  <td>{info.subscription_info.category || 'unknown'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No subscriptions found.</p>
        )}
      </div>
    </div>
  );
};

export default AnalyticsDashboard;