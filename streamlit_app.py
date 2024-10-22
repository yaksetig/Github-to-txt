import streamlit as st
import subprocess
import os
import tempfile
import shutil
from pathlib import Path

def clone_and_analyze_repo(github_url):
    """Clone a GitHub repository and analyze its code files."""
    results = []
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Clone the repository
            repo_name = github_url.split('/')[-1].replace('.git', '')
            clone_path = os.path.join(temp_dir, repo_name)
            
            # Clone the repository
            subprocess.run(['git', 'clone', github_url, clone_path], 
                         check=True, 
                         capture_output=True)

            # Define extensions to search for
            extensions = [
                "py", "js", "ts", "jsx", "tsx", "rs", "ex", "exs", "go", 
                "java", "c", "cpp", "h", "hpp", "cs", "rb", "php", "html", 
                "css", "kt", "swift", "scala", "sh", "pl", "r", "lua", "m", 
                "erl", "hs"
            ]
            
            # Find and process all matching files
            for ext in extensions:
                for file_path in Path(clone_path).rglob(f"*.{ext}"):
                    if ".git" not in str(file_path):
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                relative_path = os.path.relpath(file_path, clone_path)
                                results.append({
                                    'file': relative_path,
                                    'content': content,
                                    'extension': ext
                                })
                        except UnicodeDecodeError:
                            # Skip binary files or files with unknown encoding
                            continue
        except Exception as e:
            st.error(f"An error occurred while processing the repository: {str(e)}")
            return []

    return results

# Set up the Streamlit page
st.set_page_config(page_title="GitHub to txt", page_icon="🔍")
st.title("🔍 GitHub to txt")

st.write("""
Enter a GitHub repository URL to analyze its code files. The analyzer will collect
all code and export a txt file. Perfect for LLMs (i.e., Claude, ChatGPT).""")

# Create the GitHub URL input
github_url = st.text_input(
    "GitHub Repository URL",
    placeholder="https://github.com/username/repository"
)

# Add an analyze button
if st.button("Analyze Repository", disabled=not github_url):
    if github_url:
        with st.spinner("Analyzing repository..."):
            results = clone_and_analyze_repo(github_url)
            
            if results:
                # Display results
                st.success(f"Found {len(results)} code files!")
                
                # Create a file selector
                file_names = [r['file'] for r in results]
                selected_file = st.selectbox("Select a file to view:", file_names)
                
                # Display the selected file's content
                if selected_file:
                    file_data = next(r for r in results if r['file'] == selected_file)
                    st.code(file_data['content'], language=file_data['extension'])
                    
                # Add download button for all code
                combined_content = "\n\n".join(
                    f"### {r['file']}\n{r['content']}" for r in results
                )
                st.download_button(
                    "Download All Code",
                    combined_content,
                    file_name="repository_code.txt",
                    mime="text/plain"
                )
            else:
                st.warning("No code files found in the repository.")

# Add footer with information
st.markdown("---")
