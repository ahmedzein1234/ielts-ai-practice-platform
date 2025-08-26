'use client';

import { useState, useMemo } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  ArcElement,
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { TrendingUp, TrendingDown, Minus, Calendar, Target } from 'lucide-react';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  ArcElement
);

interface PerformanceData {
  date: string;
  speaking: number;
  writing: number;
  listening: number;
  reading: number;
  overall: number;
}

interface PerformanceChartProps {
  data: PerformanceData[];
  title?: string;
  description?: string;
  className?: string;
}

type ChartType = 'line' | 'bar' | 'doughnut';
type TimeRange = '7d' | '30d' | '90d' | '1y';

export function PerformanceChart({ data, title = 'Performance Overview', description, className }: PerformanceChartProps) {
  const [chartType, setChartType] = useState<ChartType>('line');
  const [timeRange, setTimeRange] = useState<TimeRange>('30d');
  const [selectedSkill, setSelectedSkill] = useState<string>('overall');

  const filteredData = useMemo(() => {
    const now = new Date();
    const daysToSubtract = {
      '7d': 7,
      '30d': 30,
      '90d': 90,
      '1y': 365,
    }[timeRange];

    const cutoffDate = new Date(now.getTime() - daysToSubtract * 24 * 60 * 60 * 1000);
    
    return data.filter(item => new Date(item.date) >= cutoffDate);
  }, [data, timeRange]);

  const chartData = useMemo(() => {
    const labels = filteredData.map(item => {
      const date = new Date(item.date);
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric' 
      });
    });

    const datasets = [
      {
        label: 'Speaking',
        data: filteredData.map(item => item.speaking),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
      },
      {
        label: 'Writing',
        data: filteredData.map(item => item.writing),
        borderColor: 'rgb(139, 92, 246)',
        backgroundColor: 'rgba(139, 92, 246, 0.1)',
        fill: true,
      },
      {
        label: 'Listening',
        data: filteredData.map(item => item.listening),
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        fill: true,
      },
      {
        label: 'Reading',
        data: filteredData.map(item => item.reading),
        borderColor: 'rgb(245, 158, 11)',
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        fill: true,
      },
    ];

    return { labels, datasets };
  }, [filteredData]);

  const doughnutData = useMemo(() => {
    const latestData = filteredData[filteredData.length - 1];
    if (!latestData) return null;

    return {
      labels: ['Speaking', 'Writing', 'Listening', 'Reading'],
      datasets: [
        {
          data: [latestData.speaking, latestData.writing, latestData.listening, latestData.reading],
          backgroundColor: [
            'rgba(59, 130, 246, 0.8)',
            'rgba(139, 92, 246, 0.8)',
            'rgba(16, 185, 129, 0.8)',
            'rgba(245, 158, 11, 0.8)',
          ],
          borderColor: [
            'rgb(59, 130, 246)',
            'rgb(139, 92, 246)',
            'rgb(16, 185, 129)',
            'rgb(245, 158, 11)',
          ],
          borderWidth: 2,
        },
      ],
    };
  }, [filteredData]);

  const performanceStats = useMemo(() => {
    if (filteredData.length < 2) return null;

    const current = filteredData[filteredData.length - 1];
    const previous = filteredData[filteredData.length - 2];
    const change = current.overall - previous.overall;
    const percentageChange = (change / previous.overall) * 100;

    return {
      current: current.overall,
      change,
      percentageChange,
      trend: change > 0 ? 'up' : change < 0 ? 'down' : 'stable',
    };
  }, [filteredData]);

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 9,
        ticks: {
          stepSize: 1,
        },
      },
    },
    interaction: {
      mode: 'nearest' as const,
      axis: 'x' as const,
      intersect: false,
    },
  };

  const renderChart = () => {
    switch (chartType) {
      case 'line':
        return <Line data={chartData} options={chartOptions} height={300} />;
      case 'bar':
        return <Bar data={chartData} options={chartOptions} height={300} />;
      case 'doughnut':
        return doughnutData ? <Doughnut data={doughnutData} options={{ responsive: true, maintainAspectRatio: false }} height={300} /> : null;
      default:
        return <Line data={chartData} options={chartOptions} height={300} />;
    }
  };

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              {title}
              {performanceStats && (
                <div className="flex items-center gap-1 text-sm">
                  {performanceStats.trend === 'up' && <TrendingUp className="w-4 h-4 text-green-500" />}
                  {performanceStats.trend === 'down' && <TrendingDown className="w-4 h-4 text-red-500" />}
                  {performanceStats.trend === 'stable' && <Minus className="w-4 h-4 text-gray-500" />}
                  <span className={performanceStats.trend === 'up' ? 'text-green-500' : performanceStats.trend === 'down' ? 'text-red-500' : 'text-gray-500'}>
                    {performanceStats.percentageChange > 0 ? '+' : ''}{performanceStats.percentageChange.toFixed(1)}%
                  </span>
                </div>
              )}
            </CardTitle>
            {description && <CardDescription>{description}</CardDescription>}
          </div>
          
          <div className="flex items-center gap-2">
            <Select value={timeRange} onValueChange={(value: TimeRange) => setTimeRange(value)}>
              <SelectTrigger className="w-24">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="7d">7 days</SelectItem>
                <SelectItem value="30d">30 days</SelectItem>
                <SelectItem value="90d">90 days</SelectItem>
                <SelectItem value="1y">1 year</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={chartType} onValueChange={(value: ChartType) => setChartType(value)}>
              <SelectTrigger className="w-24">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="line">Line</SelectItem>
                <SelectItem value="bar">Bar</SelectItem>
                <SelectItem value="doughnut">Doughnut</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="h-[300px]">
          {renderChart()}
        </div>
        
        {performanceStats && (
          <div className="mt-4 grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold">{performanceStats.current.toFixed(1)}</p>
              <p className="text-sm text-muted-foreground">Current Score</p>
            </div>
            <div>
              <p className="text-2xl font-bold">{performanceStats.change > 0 ? '+' : ''}{performanceStats.change.toFixed(1)}</p>
              <p className="text-sm text-muted-foreground">Change</p>
            </div>
            <div>
              <p className="text-2xl font-bold">{performanceStats.percentageChange > 0 ? '+' : ''}{performanceStats.percentageChange.toFixed(1)}%</p>
              <p className="text-sm text-muted-foreground">% Change</p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
