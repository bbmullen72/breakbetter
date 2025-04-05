import React, { useState } from 'react';
import axios from 'axios';

function GetStarted() {
  const [formData, setFormData] = useState({
    name: '',
    study_interval: 'high_mental',
    time_of_day: 'morning',
    deadline_pressure: 'low',
    personal_preferences: '',
    screen_usage: false,
    activity_level: 'sedentary',
    energy_level: 5,
    preferred_break_duration: 15
  });

  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/api/recommend', {
        ...formData,
        energy_level: parseInt(formData.energy_level),
        preferred_break_duration: parseInt(formData.preferred_break_duration)
      });

      setRecommendation(response.data);
    } catch (error) {
      console.error('Error getting recommendation:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-4xl font-bold text-gray-900 mb-8">Get Your Study & Break Recommendation</h1>

      {!recommendation ? (
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700">Name</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Study Type</label>
            <select
              name="study_interval"
              value={formData.study_interval}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            >
              <option value="high_mental">High Mental Energy (Math, Programming)</option>
              <option value="low_mental">Low Mental Energy (Reviewing Notes, Writing)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Time of Day</label>
            <select
              name="time_of_day"
              value={formData.time_of_day}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            >
              <option value="morning">Morning (Fresh)</option>
              <option value="evening">Evening (Fatigued)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Deadline Pressure</label>
            <select
              name="deadline_pressure"
              value={formData.deadline_pressure}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            >
              <option value="low">Low (No immediate deadlines)</option>
              <option value="high">High (Urgent deadlines)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Personal Preferences (comma-separated)
            </label>
            <input
              type="text"
              name="personal_preferences"
              value={formData.personal_preferences}
              onChange={handleChange}
              placeholder="e.g., reading, music, walking, meditation"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            />
            <p className="mt-1 text-sm text-gray-500">
              Enter activities you enjoy, separated by commas
            </p>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              name="screen_usage"
              checked={formData.screen_usage}
              onChange={handleChange}
              className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            />
            <label className="ml-2 block text-sm text-gray-700">
              I have been using screens
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Activity Level</label>
            <select
              name="activity_level"
              value={formData.activity_level}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            >
              <option value="sedentary">Sedentary (Mostly sitting)</option>
              <option value="active">Active (Moving around)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Energy Level (1-10)
            </label>
            <input
              type="range"
              name="energy_level"
              min="1"
              max="10"
              value={formData.energy_level}
              onChange={handleChange}
              className="mt-1 block w-full"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>Low Energy</span>
              <span>High Energy</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Preferred Break Duration (minutes)
            </label>
            <input
              type="number"
              name="preferred_break_duration"
              min="5"
              max="60"
              value={formData.preferred_break_duration}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            />
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              {loading ? 'Getting Recommendation...' : 'Get Recommendation'}
            </button>
          </div>
        </form>
      ) : (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-2xl font-bold mb-4">Your Recommendation</h2>
          <div className="space-y-4">
            <p><strong>Study Interval:</strong> {recommendation.study_interval}</p>
            <p><strong>Break Activity:</strong> {recommendation.break_activity}</p>
            <p><strong>Duration:</strong> {recommendation.duration} minutes</p>
            <div>
              <strong>Benefits:</strong>
              <ul className="list-disc list-inside mt-2">
                {recommendation.benefits.map((benefit, index) => (
                  <li key={index}>{benefit}</li>
                ))}
              </ul>
            </div>
            <div>
              <strong>Study Tips:</strong>
              <ul className="list-disc list-inside mt-2">
                {recommendation.study_tips.map((tip, index) => (
                  <li key={index}>{tip}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default GetStarted; 