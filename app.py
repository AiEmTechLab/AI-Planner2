import streamlit as st
import json
import os
from dotenv import load_dotenv
from backend.planner import create_planner
from backend.models import Plan

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Planner Agent",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    text-align: center;
    color: #2E86AB;
    margin-bottom: 2rem;
}
.success-box {
    background-color: #D4F1D4;
    border-left: 5px solid #4CAF50;
    padding: 1rem;
    margin: 1rem 0;
}
.error-box {
    background-color: #FFE6E6;
    border-left: 5px solid #F44336;
    padding: 1rem;
    margin: 1rem 0;
}
.info-box {
    background-color: #E3F2FD;
    border-left: 5px solid #2196F3;
    padding: 1rem;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🤖 AI Planner Agent</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">Transform your project brief into a comprehensive, validated plan in under 25 seconds</p>', unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key status
        api_key = os.getenv('GROQ_API_KEY')
        if api_key:
            st.success("✅ Groq API Key configured")
        else:
            st.error("❌ Groq API Key not found")
            st.info("Add your Groq API key to the .env file")
        
        st.markdown("---")
        
        # Instructions
        st.header("📖 Instructions")
        st.markdown("""
        1. **Enter your project brief** in the text area below
        2. **Click 'Generate Plan'** to create your project plan
        3. **Review the results** in both Markdown and JSON formats
        4. **Download** the plan for integration or documentation
        """)
        
        st.markdown("---")
        
        # Example briefs
        st.header("💡 Example Briefs")
        example_briefs = {
            "Mobile App": "Build a mobile expense tracking app for iOS and Android with user authentication, receipt scanning, categorization, and monthly reports.",
            "Website Redesign": "Redesign company website with modern UI/UX, improved navigation, mobile responsiveness, and integration with existing CRM system.",
            "Data Pipeline": "Create an automated data pipeline to extract customer data from multiple sources, transform it, and load into a data warehouse for analytics."
        }
        
        for name, brief in example_briefs.items():
            if st.button(f"Load {name} Example"):
                st.session_state.project_brief = brief
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📝 Project Brief")
        
        # Text input
        project_brief = st.text_area(
            "Enter your project brief:",
            height=200,
            placeholder="Describe your project in detail. Include objectives, requirements, constraints, and any specific deliverables you need...",
            key="project_brief"
        )
        
        # File upload option
        uploaded_file = st.file_uploader(
            "Or upload a text file:",
            type=['txt', 'md'],
            help="Upload a .txt or .md file containing your project brief"
        )
        
        if uploaded_file is not None:
            project_brief = uploaded_file.read().decode('utf-8')
            st.text_area("File content:", value=project_brief, height=100, disabled=True)
        
        # Generate button
        generate_button = st.button("🚀 Generate Plan", type="primary", use_container_width=True)
    
    with col2:
        st.header("📊 Generated Plan")
        
        if generate_button:
            if not project_brief.strip():
                st.error("Please enter a project brief or upload a file.")
                return
            
            if not api_key:
                st.error("Please configure your Groq API key in the .env file.")
                return
            
            # Generate plan
            with st.spinner("Generating your project plan..."):
                planner, error = create_planner()
                
                if error:
                    st.error(f"Failed to initialize planner: {error}")
                    return
                
                plan, error = planner.generate_plan(project_brief)
                
                if error:
                    st.error(f"Failed to generate plan: {error}")
                    return
                
                # Store in session state
                st.session_state.plan = plan
                st.session_state.plan_generated = True
        
        # Display results
        if hasattr(st.session_state, 'plan_generated') and st.session_state.plan_generated:
            plan = st.session_state.plan
            
            # Success message
            st.markdown('<div class="success-box">✅ Plan generated successfully!</div>', unsafe_allow_html=True)
            
            # Plan summary
            st.subheader("📋 Plan Summary")
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Total Duration", f"{plan.total_weeks} weeks")
                st.metric("Milestones", len(plan.milestones))
            with col_b:
                total_tasks = sum(len(m.tasks) for m in plan.milestones)
                st.metric("Total Tasks", total_tasks)
                st.metric("Risks Identified", len(plan.risks))
    
    # Results section (full width)
    if hasattr(st.session_state, 'plan_generated') and st.session_state.plan_generated:
        st.markdown("---")
        
        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["📄 Markdown View", "🔧 JSON View", "📊 Plan Analysis"])
        
        with tab1:
            st.subheader("Human-Readable Plan")
            markdown_content = plan.to_markdown()
            st.markdown(markdown_content)
            
            # Download button
            st.download_button(
                label="📥 Download Markdown",
                data=markdown_content,
                file_name=f"{plan.project_name.replace(' ', '_')}_plan.md",
                mime="text/markdown"
            )
        
        with tab2:
            st.subheader("Machine-Readable JSON")
            json_content = plan.model_dump_json(indent=2)
            st.code(json_content, language='json')
            
            # Download button
            st.download_button(
                label="📥 Download JSON",
                data=json_content,
                file_name=f"{plan.project_name.replace(' ', '_')}_plan.json",
                mime="application/json"
            )
        
        with tab3:
            st.subheader("Plan Analysis")
            
            # Visual milestone timeline
            st.write("**Project Timeline:**")
            
            # Create timeline visualization
            timeline_data = []
            for milestone in plan.milestones:
                total_hours = sum(task.estimated_hours for task in milestone.tasks)
                timeline_data.append({
                    'Week': milestone.week_number,
                    'Milestone': milestone.name,
                    'Tasks': len(milestone.tasks),
                    'Hours': total_hours,
                    'Description': milestone.description[:100] + "..." if len(milestone.description) > 100 else milestone.description
                })
            
            # Sort by week number
            timeline_data.sort(key=lambda x: x['Week'])
            
            # Display timeline as interactive chart
            col_timeline, col_details = st.columns([2, 1])
            
            with col_timeline:
                # Create a visual timeline using Streamlit's native chart
                import pandas as pd
                df = pd.DataFrame(timeline_data)
                
                # Bar chart showing hours per milestone
                st.bar_chart(df.set_index('Milestone')['Hours'])
                
                # Timeline visualization using custom HTML/CSS
                timeline_html = """
                <div style="position: relative; margin: 20px 0;">
                    <div style="position: absolute; left: 50px; top: 0; bottom: 0; width: 2px; background-color: #2E86AB;"></div>
                """
                
                for i, milestone in enumerate(timeline_data):
                    position = i * 120
                    timeline_html = ""
                for entry in timeline_data:
                    timeline_html += f"""
                <div style="position: relative; margin: 20px 0; display: flex; align-items: center;">
                <div style="width: 40px; text-align: center; font-weight: bold; color: #2E86AB;">W{entry['Week']}</div>
                <div style="width: 20px; height: 20px; border-radius: 50%; background-color: #2E86AB; margin: 0 10px; z-index: 1;"></div>
                <div style="flex: 1; background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-left: 10px;">
                    <div style="font-weight: bold; color: #2E86AB;">{entry['Milestone']}</div>
                    <div style="font-size: 12px; color: #666; margin-top: 5px;">{entry['Description']}</div>
                    <div style="font-size: 11px; color: #888; margin-top: 5px;">{entry['Tasks']} tasks • {entry['Hours']} hours</div>
                </div>
                </div>
                """
                
                timeline_html += "</div>"
                st.markdown(timeline_html, unsafe_allow_html=True)
            
            with col_details:
                st.write("**Timeline Summary:**")
                for milestone in timeline_data:
                    with st.expander(f"Week {milestone['Week']}: {milestone['Milestone']}"):
                        st.write(f"**Description:** {milestone['Description']}")
                        st.write(f"**Tasks:** {milestone['Tasks']}")
                        st.write(f"**Estimated Hours:** {milestone['Hours']}")
                        
                        # Show actual tasks
                        actual_milestone = next(m for m in plan.milestones if m.name == milestone['Milestone'])
                        st.write("**Task Breakdown:**")
                        for task in actual_milestone.tasks:
                            parallel_indicator = "🔄" if task.can_parallel else "📋"
                            st.write(f"{parallel_indicator} {task.name} ({task.estimated_hours}h)")
            
            st.markdown("---")
            
            # Additional analysis
            col_left, col_right = st.columns(2)
            
            with col_left:
                # Parallel opportunities
                if plan.parallel_opportunities:
                    st.write("**🔄 Parallel Work Opportunities:**")
                    for opportunity in plan.parallel_opportunities:
                        st.write(f"• {opportunity}")
                
                # Task distribution
                st.write("**📊 Task Distribution:**")
                total_tasks = sum(len(m.tasks) for m in plan.milestones)
                total_hours = sum(sum(task.estimated_hours for task in m.tasks) for m in plan.milestones)
                st.metric("Total Tasks", total_tasks)
                st.metric("Total Hours", total_hours)
                st.metric("Average Hours per Task", f"{total_hours/total_tasks:.1f}" if total_tasks > 0 else "0")
            
            with col_right:
                # Risk assessment
                st.write("**⚠️ Risk Assessment:**")
                for risk in plan.risks:
                    risk_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
                    impact_icon = risk_color.get(risk.impact, "🟡")
                    prob_icon = risk_color.get(risk.probability, "🟡")
                    st.write(f"**{risk.title}**")
                    st.write(f"Impact: {impact_icon} {risk.impact} | Probability: {prob_icon} {risk.probability}")
                    with st.expander("Mitigation Strategy"):
                        st.write(risk.mitigation)

if __name__ == "__main__":
    main()