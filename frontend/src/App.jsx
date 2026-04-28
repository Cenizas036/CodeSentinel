import React from 'react';
import BackgroundGlow from './components/BackgroundGlow';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import Analyzer from './components/Analyzer';
import FeatureGrid from './components/FeatureGrid';
import BenchmarkTable from './components/BenchmarkTable';
import CTA from './components/CTA';
import Footer from './components/Footer';

function App() {
  return (
    <>
      <BackgroundGlow />
      <Navbar />
      <main>
        <Hero />
        <Analyzer />
        <FeatureGrid />
        <BenchmarkTable />
        <CTA />
      </main>
      <Footer />
    </>
  );
}

export default App;
