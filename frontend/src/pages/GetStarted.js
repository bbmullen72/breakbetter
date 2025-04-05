import React, { useState } from 'react';
import axios from 'axios';

function GetStarted() {
  const [formData, setFormData] = useState({
    name: '',
    study_interval: 'high_mental',
    time_of_day: 'morning',
    deadline_pressure: 'low',
    personal_preferences: [],
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

  const handlePreferenceChange = (e) => {
    const { value, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      personal_preferences: checked
        ? [...prev.personal_preferences, value]
        : prev.personal_preferences.filter(pref => pref !== value)
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
              <option value="low">Low (Plenty of Time)</option>
              <option value="high">High (Deadline Soon)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Personal Preferences</label>
            <div className="mt-2 space-y-2">
              {['music', 'sports', 'reading', 'meditation', 'walking', 'napping'].map((pref) => (
                <label key={pref} className="inline-flex items-center">
                  <input
                    type="checkbox"
                    value={pref}
                    checked={formData.personal_preferences.includes(pref)}
                    onChange={handlePreferenceChange}
                    className="rounded border-gray-300 text-indigo-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">{pref.charAt(0).toUpperCase() + pref.slice(1)}</span>
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Were you using screens?
            </label>
            <div className="mt-2">
              <label className="inline-flex items-center">
                <input
                  type="checkbox"
                  name="screen_usage"
                  checked={formData.screen_usage}
                  onChange={handleChange}
                  className="rounded border-gray-300 text-indigo-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                />
                <span className="ml-2 text-sm text-gray-700">Yes</span>
              </label>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Activity Level</label>
            <select
              name="activity_level"
              value={formData.activity_level}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            >
              <option value="sedentary">Sedentary (Sitting for long periods)</option>
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
            <div className="text-sm text-gray-500">{formData.energy_level}</div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Preferred Break Duration (minutes)
            </label>
            <input
              type="number"
              name="preferred_break_duration"
              value={formData.preferred_break_duration}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          >
            {loading ? 'Getting Recommendation...' : 'Get Recommendation'}
          </button>
        </form>
      ) : (
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Your Study & Break Recommendation</h2>
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-medium text-gray-900">Recommended Study Interval</h3>
              <p className="text-gray-600">{recommendation.study_interval}</p>
            </div>
            <div>
              <h3 className="text-lg font-medium text-gray-900">Break Activity</h3>
              <p className="text-gray-600">{recommendation.break_activity}</p>
            </div>
            <div>
              <h3 className="text-lg font-medium text-gray-900">Duration</h3>
              <p className="text-gray-600">{recommendation.duration} minutes</p>
            </div>
            <div>
              <h3 className="text-lg font-medium text-gray-900">Description</h3>
              <p className="text-gray-600">{recommendation.description}</p>
            </div>
            <div>
              <h3 className="text-lg font-medium text-gray-900">Benefits</h3>
              <ul className="list-disc list-inside text-gray-600">
                {recommendation.benefits.map((benefit, index) => (
                  <li key={index}>{benefit}</li>
                ))}
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-medium text-gray-900">Study Tips</h3>
              <ul className="list-disc list-inside text-gray-600">
                {recommendation.study_tips.map((tip, index) => (
                  <li key={index}>{tip}</li>
                ))}
              </ul>
            </div>
          </div>
          <button
            onClick={() => setRecommendation(null)}
            className="mt-6 bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          >
            Get Another Recommendation
          </button>
        </div>
      )}
    </div>
  );
}

export default GetStarted; 