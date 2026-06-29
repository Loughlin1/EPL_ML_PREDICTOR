import { useEffect, useState } from 'react';
import { getModelExplanation } from '../api';

function CollapsibleCard({ title, children, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between px-4 py-3 text-left bg-gray-50 hover:bg-gray-100 transition-colors"
      >
        <span className="text-sm font-semibold text-gray-800">{title}</span>
        <svg
          className={`w-4 h-4 text-gray-400 transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {open && <div className="px-4 py-3 text-sm text-gray-700 space-y-2">{children}</div>}
    </div>
  );
}

function ModelExplanation() {
  const [explanation, setExplanation] = useState(null);
  const [workflow, setWorkflow] = useState(null);

  useEffect(() => {
    getModelExplanation()
      .then((res) => {
        setExplanation(res.data.content.model_explanation);
        setWorkflow(res.data.content.model_workflow);
      })
      .catch((err) => console.error('Error fetching model explanation:', err));
  }, []);

  if (!explanation && !workflow) return null;

  return (
    <div className="w-full max-w-3xl mt-4 space-y-6">
      {explanation && (
        <div>
          <h2 className="text-base font-semibold text-gray-900 mb-1">{explanation.title}</h2>
          <p className="text-sm text-gray-500 mb-3">{explanation.description}</p>
          <div className="space-y-2">
            {explanation.points.map((point, i) => (
              <CollapsibleCard key={i} title={point.title}>
                <ul className="list-disc pl-4 space-y-1">
                  {point.subpoints.map((sp, j) => (
                    <li key={j}>{sp}</li>
                  ))}
                </ul>
              </CollapsibleCard>
            ))}
          </div>
        </div>
      )}

      {workflow && (
        <div>
          <h2 className="text-base font-semibold text-gray-900 mb-1">{workflow.title}</h2>
          <p className="text-sm text-gray-500 mb-3">{workflow.description}</p>
          <div className="space-y-2">
            {workflow.steps.map((step, i) => (
              <CollapsibleCard key={i} title={`${i + 1}. ${step.title}`}>
                <ul className="list-disc pl-4 space-y-1">
                  {step.substeps.map((ss, j) => (
                    <li key={j}>{ss}</li>
                  ))}
                </ul>
              </CollapsibleCard>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default ModelExplanation;
