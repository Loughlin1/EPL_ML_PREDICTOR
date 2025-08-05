import React, { useEffect, useState } from 'react';
import { getModelExplanation } from '../api';

function ModelExplanation() {
  const [explanation, setExplanation] = useState(null);
  const [workflow, setWorkflow] = useState(null);
  const [githubLink, setGithubLink] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
          const response = await getModelExplanation();
          setExplanation(response.data.content.model_explanation);
          setWorkflow(response.data.content.model_workflow);
      } catch (error) {
        console.error('Error fetching initial data:', error);
      }
      };
      fetchData();
  }, []);

  return (
    <div className='max-w-3xl'>
      {explanation && (
        <div>
          <h2 className="text-base md:text-xl font-semibold whitespace-nowrap pt-5">
            {explanation.title}
          </h2>
          <p className='pt-3 pb-3'>{explanation.description}</p>
          <ol className="list-decimal pl-5"> 
            {explanation.points.map((point, index) => (
              <li key={index}>
                <div>
                  <p className="text-sm md:text-l"><strong>{point.title}</strong></p>
                  <ul className='list-disc pl-5 text-sm'>
                    {(point.subpoints).map(subpoint => (
                      <li key={subpoint}>{subpoint}</li>
                    ))}
                  </ul>
                </div>
              </li>
            ))}
          </ol>
        </div>
      )}
      {workflow && (
        <div>
          <h2 className="text-base md:text-xl font-semibold whitespace-nowrap pt-5">{workflow.title}</h2>
          <p className='pt-3 pb-3'>{workflow.description}</p>
          <ol className="list-decimal pl-5"> 
            {workflow.steps.map((step, index) => (
              <li key={index}>
                <div>
                  <p className="text-sm md:text-l"><strong>{step.title}</strong></p>
                  <ul className='list-disc pl-5 text-sm'>
                    {(step.substeps).map(substep => (
                      <li key={substep}>{substep}</li>
                    ))}
                  </ul>
                </div>
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}

export default ModelExplanation;
