import { useState } from 'react';


function CollapsibleHeader({default_state, title, content}) {
  const [isCollapsed, setIsCollapsed] = useState(default_state);
  const toggleCollapse = () => {
    setIsCollapsed(!isCollapsed);
  };


  return (
    <div>
      <h4 onClick={toggleCollapse} className="collapsibleHeader">
        {isCollapsed ? '▶' : '▼'} {title}
      </h4>
      {!isCollapsed && <div>{content}</div> }
    </div>
  );
}
export default CollapsibleHeader;