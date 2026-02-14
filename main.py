import streamlit as st
import pandas as pd
import numpy as np

from modules.instruction_parser import InstructionParser
import plotly.express as px
import plotly.graph_objects as go
from modules.data_profiling import DataProfiler
from modules.ai_suggestions import AISuggestionEngine
from modules.data_cleaning import DataCleaner
from modules.report_generator import ReportGenerator
from utils.helpers import format_number, get_data_quality_score
import io
import base64
# Page configuration
st.set_page_config(
    page_title="AI Data Cleaning System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .suggestion-box {
        background-color: #e8f4fd;
        border-left: 5px solid #1f77b4;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">🤖 AI-Assisted Data Cleaning System</h1>', 
                unsafe_allow_html=True)
    
    # Initialize session state
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'cleaned_data' not in st.session_state:
        st.session_state.cleaned_data = None
    if 'profiling_results' not in st.session_state:
        st.session_state.profiling_results = None
    if 'suggestions' not in st.session_state:
        st.session_state.suggestions = None
    if 'cleaning_report' not in st.session_state:
        st.session_state.cleaning_report = None

    # Sidebar
    st.sidebar.title("📊 Navigation")
    
    # File Upload Module
    st.sidebar.markdown("### 📁 File Upload")
    uploaded_file = st.sidebar.file_uploader(
        "Choose a file", 
        type=['csv', 'xlsx', 'xls'],
        help="Upload CSV or Excel files"
    )
    
    if uploaded_file is not None:
        try:
            # Load data
            if uploaded_file.name.endswith('.csv'):
                st.session_state.data = pd.read_csv(uploaded_file)
            else:
                st.session_state.data = pd.read_excel(uploaded_file)
            
            st.sidebar.success(f"✅ File uploaded successfully!")
            st.sidebar.info(f"📏 Shape: {st.session_state.data.shape}")
            
        except Exception as e:
            st.sidebar.error(f"❌ Error loading file: {str(e)}")
            return

    # Main content
    if st.session_state.data is not None:
        # Tabs for different modules
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📋 Data Overview", 
            "🔍 Data Profiling", 
            "🤖 AI Suggestions", 
            "🧹 Data Cleaning", 
            "📊 Summary Report"
        ])
        
        with tab1:
            display_data_overview()
        
        with tab2:
            display_data_profiling()
        
        with tab3:
            display_ai_suggestions()
        
        with tab4:
            display_data_cleaning()
        
        with tab5:
            display_summary_report()
    
    else:
        st.info("👆 Please upload a CSV or Excel file to get started!")
        
        # Show sample data information
        st.markdown("### 📝 Sample Data Format")
        st.markdown("""
        Your data should be in CSV or Excel format with:
        - Column headers in the first row
        - Consistent data types per column
        - Any encoding (UTF-8 recommended)
        """)

def display_data_overview():
    """Display basic data overview"""
    st.header("📋 Dataset Overview")
    
    data = st.session_state.data
    
    # Basic metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📏 Total Rows", format_number(data.shape[0]))
    with col2:
        st.metric("📊 Total Columns", data.shape[1])
    with col3:
        st.metric("💾 Memory Usage", f"{data.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
    with col4:
        quality_score = get_data_quality_score(data)
        st.metric("✨ Data Quality", f"{quality_score:.1f}%")
    
    # Data preview
    st.subheader("🔍 Data Preview")
    # Add row selector
    # Add row selector
    num_rows = st.slider(
    "Select number of rows to preview",
    min_value=5,
    max_value=len(data),
    value=10,
    key="cleaned_preview_slider"
)

    st.dataframe(data.head(num_rows), use_container_width=True)


    
    # Data types
    st.subheader("📋 Column Information")
    col_info = pd.DataFrame({
        'Column': data.columns,
        'Data Type': data.dtypes.astype(str),
        'Non-Null Count': data.count(),
        'Null Count': data.isnull().sum(),
        'Null Percentage': (data.isnull().sum() / len(data) * 100).round(2)
    })
    st.dataframe(col_info, use_container_width=True)

def display_data_profiling():
    """Display comprehensive data profiling"""
    st.header("🔍 Data Profiling Analysis")
    
    data = st.session_state.data
    profiler = DataProfiler()
    
    # Generate profiling results
    if st.session_state.profiling_results is None:
        with st.spinner("🔄 Analyzing your data..."):
            st.session_state.profiling_results = profiler.generate_profile(data)
    
    results = st.session_state.profiling_results
    
    # Missing values analysis
    st.subheader("❌ Missing Values Analysis")
    if results['missing_values']['total_missing'] > 0:
        missing_df = pd.DataFrame(results['missing_values']['by_column']).T
        missing_df.columns = ['Count', 'Percentage']
        missing_df = missing_df[missing_df['Count'] > 0].sort_values('Count', ascending=False)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.dataframe(missing_df, use_container_width=True)
        
        with col2:
            fig = px.bar(
                x=missing_df.index, 
                y=missing_df['Percentage'],
                title="Missing Values by Column (%)",
                labels={'x': 'Columns', 'y': 'Missing Percentage'}
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("✅ No missing values found!")
    
    # Duplicates analysis
    st.subheader("🔄 Duplicate Analysis")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Duplicate Rows", results['duplicates']['count'])
    with col2:
        st.metric("Duplicate Percentage", f"{results['duplicates']['percentage']:.2f}%")
    
    # Outliers analysis
    st.subheader("📈 Outliers Analysis")
    numeric_columns = data.select_dtypes(include=[np.number]).columns
    
    if len(numeric_columns) > 0:
        outlier_summary = []
        for col in numeric_columns:
            if col in results['outliers']:
                outlier_summary.append({
                    'Column': col,
                    'Outliers Count': results['outliers'][col]['count'],
                    'Outliers Percentage': f"{results['outliers'][col]['percentage']:.2f}%"
                })
        
        if outlier_summary:
            outlier_df = pd.DataFrame(outlier_summary)
            st.dataframe(data, use_container_width=True)

            
            # Outlier visualization
            selected_col = st.selectbox("Select column for outlier visualization:", numeric_columns)
            if selected_col in results['outliers']:
                fig = go.Figure()
                fig.add_trace(go.Box(y=data[selected_col], name=selected_col))
                fig.update_layout(title=f"Box Plot for {selected_col} (Outliers Detection)")
                st.plotly_chart(fig, use_container_width=True)
    
    # Categorical inconsistencies
    st.subheader("🔤 Categorical Inconsistencies")
    if results['categorical_issues']:
        for col, issues in results['categorical_issues'].items():
            if issues:
                st.write(f"**{col}:**")
                st.write(f"Unique values: {issues['unique_values']}")
                if issues['case_issues']:
                    st.warning(f"Potential case inconsistencies detected: {issues['case_issues']}")

def display_ai_suggestions():
    """Display AI-generated suggestions"""
    st.header("🤖 AI Cleaning Suggestions")
    
    if st.session_state.profiling_results is None:
        st.warning("⚠️ Please run data profiling first!")
        return
    
    # Generate suggestions
    if st.session_state.suggestions is None:
        suggestion_engine = AISuggestionEngine()
        st.session_state.suggestions = suggestion_engine.generate_suggestions(
            st.session_state.data, 
            st.session_state.profiling_results
        )
    
    suggestions = st.session_state.suggestions
    
    if not suggestions:
        st.success("🎉 Your data looks clean! No major issues detected.")
    else:
        st.markdown("### 💡 Recommended Actions")
        
        for suggestion in suggestions:
            with st.expander(f"🔧 {suggestion['title']}", expanded=True):
                st.markdown(f"**Priority:** {suggestion['priority']}")
                st.markdown(f"**Issue:** {suggestion['description']}")
                st.markdown(f"**Recommendation:** {suggestion['recommendation']}")
                
                if suggestion['type'] == 'missing_values':
                    st.info(f"📊 Affected columns: {', '.join(suggestion['affected_columns'])}")
                elif suggestion['type'] == 'duplicates':
                    st.info(f"🔄 {suggestion['count']} duplicate rows found")
                elif suggestion['type'] == 'outliers':
                    st.info(f"📈 Outliers detected in: {', '.join(suggestion['affected_columns'])}")

    # ---------------------------------------------------
    # 🎤 Voice-Based Data Instructions (INSIDE FUNCTION)
    # ---------------------------------------------------

    st.markdown("---")
    st.subheader("🎤 Voice-Based Data Instructions")

    audio_file = st.file_uploader(
        "Upload client audio/video instruction",
        type=["mp3", "wav", "m4a", "mp4"],
        key="voice_upload"
    )

    if audio_file is not None:

        from modules.voice_service import VoiceService
        from modules.instruction_parser import InstructionParser

        voice_service = VoiceService()

        with st.spinner("🔄 Transcribing audio..."):
            instruction_text = voice_service.transcribe(audio_file)

        st.success("Transcription Complete ✅")
        st.text_area("Extracted Instructions", instruction_text, height=150)
def display_data_cleaning():
    st.header("🧹 Data Cleaning")

    if "data" not in st.session_state:
        st.warning("⚠️ Please upload data first.")
        return

    st.write("Data Preview:")
    st.dataframe(st.session_state.data)

    if st.button("Run Cleaning"):
        # Example dummy cleaning logic
        cleaned_data = st.session_state.data.drop_duplicates()
        cleaning_report = {
            "rows_removed": len(st.session_state.data) - len(cleaned_data)
        }

        st.session_state.cleaned_data = cleaned_data
        st.session_state.cleaning_report = cleaning_report

        st.success("✅ Cleaning completed!")


def display_summary_report():


    """Display comprehensive summary report"""
    st.header("📊 Data Cleaning Summary Report")
    
    if st.session_state.cleaning_report is None:
        st.info("🔄 No cleaning operations performed yet. Please clean your data first.")
        return
    
    report_generator = ReportGenerator()
    report = report_generator.generate_report(
        st.session_state.data,
        st.session_state.cleaned_data,
        st.session_state.cleaning_report
    )
    
    # Display metrics
    st.subheader("📈 Key Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Rows Processed", format_number(report['original_shape'][0]))
        st.metric("Rows Removed", format_number(report['rows_removed']))
    
    with col2:
        st.metric("Columns Processed", report['original_shape'][1])
        st.metric("Columns Removed", report['columns_removed'])
    
    with col3:
        st.metric("Missing Values Fixed", format_number(report['missing_values_handled']))
        st.metric("Duplicates Removed", format_number(report['duplicates_removed']))
    
    # Detailed operations
    st.subheader("🔧 Operations Performed")
    
    operations = report['operations_performed']
    for operation in operations:
        st.success(f"✅ {operation}")
    
    # Quality improvement
    st.subheader("✨ Quality Improvement")
    
    improvement = report['quality_improvement']
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Original Quality Score", f"{improvement['original_score']:.1f}%")
    with col2:
        st.metric(
            "Final Quality Score", 
            f"{improvement['final_score']:.1f}%",
            delta=f"{improvement['improvement']:.1f}%"
        )
    
    # Progress visualization
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = improvement['final_score'],
        delta = {'reference': improvement['original_score']},
        title = {'text': "Data Quality Score"},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 80], 'color': "gray"},
                {'range': [80, 100], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Download report
    st.json(report)
    
    st.download_button(
    label="📥 Download Summary Report",
    data=str(report),
    file_name="data_cleaning_report.txt",
    mime="text/plain"
)

if __name__ == "__main__":
    main()

