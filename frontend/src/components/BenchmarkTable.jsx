import React, { useEffect, useState, useRef } from 'react';
import './BenchmarkTable.css';

const CountUp = ({ end, duration = 2000, suffix = '', prefix = '' }) => {
  const [count, setCount] = useState(0);
  const ref = useRef(null);
  const [hasAnimated, setHasAnimated] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !hasAnimated) {
          setHasAnimated(true);
        }
      },
      { threshold: 0.3 }
    );
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [hasAnimated]);

  useEffect(() => {
    if (!hasAnimated) return;
    let startTimestamp = null;
    let animId;
    const step = (timestamp) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      const easeProgress = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
      setCount(Math.floor(easeProgress * end));
      if (progress < 1) {
        animId = window.requestAnimationFrame(step);
      }
    };
    animId = window.requestAnimationFrame(step);
    return () => window.cancelAnimationFrame(animId);
  }, [hasAnimated, end, duration]);

  return <span ref={ref}>{prefix}{count.toLocaleString()}{suffix}</span>;
};

const PulseCheck = () => (
  <div className="benchmark__check">
    <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
    </svg>
  </div>
);

const BenchmarkTable = () => {
  const data = [
    { metric: 'Cold Start Time', legacy: 1200, ours: 12, legacySuffix: 'ms', oursSuffix: 'ms' },
    { metric: 'Memory Footprint', legacy: 450, ours: 45, legacySuffix: 'MB', oursSuffix: 'MB' },
    { metric: 'Concurrent Users', legacy: 1000, ours: 50000, legacySuffix: '', oursSuffix: '+' },
    { metric: 'Bundle Size', legacy: 250, ours: 24, legacySuffix: 'kb', oursSuffix: 'kb' },
    { metric: 'API Latency (p99)', legacy: 340, ours: 12, legacySuffix: 'ms', oursSuffix: 'ms' },
  ];

  return (
    <section className="benchmark" id="performance">
      <div className="container">
        <div className="benchmark__header">
          <span className="tech-label text-emerald">Benchmarks</span>
          <h2 className="benchmark__title font-serif">Metrics that Matter</h2>
          <p className="benchmark__subtitle text-muted">
            Real-world performance data. No synthetic benchmarks, no asterisks.
          </p>
        </div>

        <div className="benchmark__table-wrap glass-panel">
          <table className="benchmark__table">
            <thead>
              <tr>
                <th className="tech-label text-left">Metric</th>
                <th className="tech-label text-right">Legacy System</th>
                <th className="tech-label text-right">CodeSentinel</th>
                <th className="tech-label text-center">Status</th>
              </tr>
            </thead>
            <tbody>
              {data.map((row, i) => (
                <tr key={i} className="benchmark__row">
                  <td className="benchmark__metric">{row.metric}</td>
                  <td className="font-mono text-muted text-right">
                    <CountUp end={row.legacy} suffix={row.legacySuffix} />
                  </td>
                  <td className="font-mono text-emerald text-right">
                    <CountUp end={row.ours} suffix={row.oursSuffix} />
                  </td>
                  <td className="text-center">
                    <PulseCheck />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
};

export default BenchmarkTable;
