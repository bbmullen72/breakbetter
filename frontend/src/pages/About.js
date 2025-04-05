import React from 'react';

function About() {
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-4xl font-bold text-gray-900 mb-8">About BreakBetter</h1>
      
      <div className="space-y-6">
        <section>
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">What is BreakBetter?</h2>
          <p className="text-gray-600 leading-relaxed">
            BreakBetter is an AI-powered application designed to help you take better breaks. 
            In today's fast-paced world, taking effective breaks is crucial for maintaining 
            productivity and well-being. Our platform uses advanced AI to analyze your profile 
            and provide personalized break recommendations that suit your needs and preferences.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Why We Created BreakBetter</h2>
          <p className="text-gray-600 leading-relaxed">
            We noticed that many people struggle with taking effective breaks. Either they 
            don't take breaks at all, or they take breaks that don't actually help them 
            recharge. BreakBetter aims to solve this problem by providing personalized, 
            science-backed break recommendations that help you return to work feeling 
            refreshed and productive.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">How It Works</h2>
          <ol className="list-decimal list-inside space-y-4 text-gray-600">
            <li>Create your profile by providing basic information about yourself</li>
            <li>Tell us about your current stress level and available time</li>
            <li>Our AI analyzes your profile and preferences</li>
            <li>Receive personalized break recommendations</li>
            <li>Take better breaks and improve your productivity</li>
          </ol>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Our Mission</h2>
          <p className="text-gray-600 leading-relaxed">
            Our mission is to help people maintain a healthy work-life balance by taking 
            effective breaks. We believe that better breaks lead to better productivity, 
            improved mental health, and overall well-being.
          </p>
        </section>
      </div>
    </div>
  );
}

export default About; 