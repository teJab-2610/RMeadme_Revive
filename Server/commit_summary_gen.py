from Keys import GEMINI_API_KEY
import google.generativeai as genai

shared_prompt = """You are an expert programmer, and you are trying to summarize a git diff.
                    Reminders about the git diff format:
                    For every file, there are a few metadata lines, like (for example):
                    \\\`
                    diff --git a/lib/index.js b/lib/index.js
                    index aadf691..bfef603 100644
                    --- a/lib/index.js
                    +++ b/lib/index.js
                    \\\`
                    This means that \lib/index.js\ was modified in this commit. Note that this is only an example.
                    Then there is a specifier of the lines that were modified.
                    A line starting with \+\ means it was added.
                    A line that starting with \-\ means that line was deleted.
                    A line that starts with neither \+\ nor \-\ is code given for context and better understanding.
                    It is not part of the diff.
                    """

class SummaryGenerator_Gemini:

  def __init__(self):
    genai.configure(api_key=GEMINI_API_KEY)
    self.model = genai.GenerativeModel('gemini-pro')

  def extract_contents(self, fpath):
    with open(fpath, 'r') as file:
      contents = file.read()
    return contents
  
  def test(self):
    response = self.model.generate_content("One line answer to what is life.")
    if response.text:
      return 1

  def promt_response(self, prompt, graph_before, graph_after, graph_type):
    response = self.model.generate_content(prompt +" "+graph_type+"  of code before commit : "+graph_before+"  "+graph_type + " of code after commit : "+ graph_after)
    return response.text


  def commit_summary(self, method_wise_summaries, issue_title = None):

    prompt =     """
    I have a commit in which some number of methods changed. Summarise the commit and tell me what type of commit it might be from the following categories like "Bugfix", "Feature", "Dependencies", "Platform Support".
    Here "Bugfix" means anything related to fixing bugs or errors in the code.
    "Feature" means anything related to increasing functionality or features in the software
    "Dependencies" means anything related to solving current dependency issues
    "Platform Support" means anything related to increasing usability of the software on different platforms like linux and windows or ios and android"
    """
    if(issue_title):
      prompt+= "The commit is linked to the issue titled, "+ issue_title

    prompt+= "Below I am giving you the summaries of different methods that got changed."

    for single_method_sumamry in method_wise_summaries:
      prompt+= single_method_sumamry

    response = self.model.generate_content(prompt)
    commit_summary = response.text
    return commit_summary

  def method_summary(self,method_bf,method_af):
    if(method_bf==None ):
      method_bf=""
    if(method_af==None ):
      method_af=""
    prompt= """" I have two versions of method code before and after a commit , give me key differences as simple as possible, without losing much, in software engineer point of view, method before : """
    prompt=prompt+method_bf+"\n"+"method after: "+method_af
    response = self.model.generate_content(prompt)
    method_summary = response.text
    # print(f"\n\n method: \n {method_summary} ")
    return method_summary

  def file_summary(self,fileName,file_bf,file_af,all_modified_methods_summaries):
    prompt= """" I have two versions of file code before and after a commit and summaries of changes in the file's methods , give me key differences as simple as possible without losing much, in software engineer point of view, file before : """
    prompt=prompt+file_bf+"\n"+"file after: "+file_af
    for f,methodName,method_summary in all_modified_methods_summaries:
      prompt = prompt+"\n"+methodName+" change summary : \n"+method_summary
    response = self.model.generate_content(prompt)
    file_summary = response.text
    # print(f"\n\n\n file {fileName} : \n {file_summary} ")
    return file_summary

  def file_summary_individual(self,fileName,file_bf,file_af):
        prompt= """" I have two versions of file code before and after a commit.
          File before commit:
          """+file_bf+"""

          File after commit:
          """+file_af+"""

          Please summarize it in a comment, describing the changes made in the diff in high level.
          Do it in the following way:
          Write the file name and then write a brief summary of changes of what happend in the file. Keep it simple which can help a software engineer understand easily. """
        prompt=prompt+file_bf+"\n"+"file after: "+file_af
        # for f,methodName,method_summary in all_modified_methods_summaries:
        #   prompt = prompt+"\n"+methodName+" change summary : \n"+method_summary
        response = self.model.generate_content(prompt)
        file_summary = response.text
        # print(f"\n\n\n file: \n ")
        return file_summary

  def file_summary_fdiff(self,fileName,file_diff):
      # prompt= """" I have two versions of file code before and after a commit , give me key differences as concisely as possible in software engineer point of view, file before : """
      prompt="""You are an expert programmer, and you are trying to summarize a git diff.
        Reminders about the git diff format:
        For every file, there are a few metadata lines, like (for example):
        \\\`
        diff --git a/lib/index.js b/lib/index.js
        index aadf691..bfef603 100644
        --- a/lib/index.js
        +++ b/lib/index.js
        \\\`
        This means that \lib/index.js\ was modified in this commit. Note that this is only an example.
        Then there is a specifier of the lines that were modified.
        A line starting with \+\ means it was added.
        A line that starting with \-\ means that line was deleted.
        A line that starts with neither \+\ nor \-\ is code given for context and better understanding.
        It is not part of the diff.

        The following is a git diff of a single file. """+file_diff+"""
        Please summarize it in a comment, describing the changes made in the diff in high level.
        Do it in the following way:
        Write the file name and then write a brief summary of changes of what happend in the file. Keep it simple which can help a software engineer understand easily."""
      # for f,methodName,method_summary in all_modified_methods_summaries:
      #   prompt = prompt+"\n"+methodName+" change summary : \n"+method_summary
      response = self.model.generate_content(prompt)
      file_summary = response.text
      # print(f"\n\n\n file: \n ")
      return file_summary

  # def commit_summary_code(self,commit_msg,file_summaries):
  #   prompt= """"
  #   I have file change summaries before and after a commit and commit message , give me key differences as concisely as possible in software engineer point of view,
  #   Summarise the commit and tell me what type of commit it might be from the following categories like "Bugfix", "Feature", "Dependencies", "Platform Support".
  #    Here "Bugfix" means anything related to fixing bugs or errors in the code.
  #    "Feature" means anything related to increasing functionality or features in the software
  #    "Dependencies" means anything related to solving current dependency issues
  #    "Platform Support" means anything related to increasing usability of the software on different platforms like linux and windows or ios and android"

  #   """
  #   # prompt = """
  #   # I have a commit in which some number of methods changed. Summarise the commit and tell me what type of commit it might be from the following categories like "Bugfix", "Feature", "Dependencies", "Platform Support".
  #   # Here "Bugfix" means anything related to fixing bugs or errors in the code.
  #   # "Feature" means anything related to increasing functionality or features in the software
  #   # "Dependencies" means anything related to solving current dependency issues
  #   # "Platform Support" means anything related to increasing usability of the software on different platforms like linux and windows or ios and android"
  #   # """
  #   for fileName , file_summary in file_summaries:
  #     prompt= prompt + "\nIn this file" + fileName + " the changes have been summarized like this : \n"+file_summary
  #   prompt=prompt+"\n Commit message : "+commit_msg+" don't give seperated file summaries"
  #   # print(prompt)
  #   response = model.generate_content(prompt)
  #   commit_summary = response.text
  #   # print("Commit summary: ", commit_summary)
  #   # print(f"\n\n\n\n\n\n commit : \n {commit_summary} ")
  #   return commit_summary

  # def commit_summary_code_diff(self,commit_msg,file_summaries,FILE_SUMMARIES_BASED_ON_RAW_GIT_DIFF):
  #   file_summary=""
  #   file_summaries_diff=""
  #   for fn,fs in file_summaries:
  #     file_summary=file_summary+fn+" :\n"+fs+"\n"
  #   for fn,fs in FILE_SUMMARIES_BASED_ON_RAW_GIT_DIFF:
  #     file_summaries_diff=file_summaries_diff+fn+" :\n"+fs+"\n"
  #   prompt="""
  #     In a given commmit, the summaries of changes in files generated based on before and after files are gives as\n"""+file_summary+"""and the summaries based on only the raw git diffs is gives as\n"""+file_summaries_diff+""".
  #     The commit message given by the user for this commit is : """+commit_msg+""".
  #     Now based on both the summaries, on a high level summaries the overall commit into one or multiple of following categories in software engineer point of view. 
  #     For exaple if a commit is of the type bug fix and dependencies, give only two lines one for the bug fix and one for the tests, with bug fix and tests between dollar sign like $bug fix$ and $tests$ with a very small and brief explnation for each
  #     But don't repeat words. For example say there is a dependency change, dont repreat dependency word like "Dependency Update: Dependency updated from x to y." Say "Dependency Update: Package version from x to y". Similarly for other categories too. 
  #     Also if there is commit related to documentation, try classifying the commit in to any of the below categories. Say if the documentation is related to the
  #     software support on linux, categorise it into Support. Similarly if the documentation talks about setting up software, categorize it into installation. Say "Installation".
  #     If the documentation is related to test code snippets or test cases, categorize it into "Tests". 
  #     If the documentation is related to the code style or code formatting, categorize it into "Style". 
  #     If the documentation is related giving any envirorment variables or commands related to setting up the software, categorize it into "Configuration".
  #     If the documentation is related to any security measures or security vulnerabilities, categorize it into "Security".
  #     Do not make documentation related commits as a separate category. Given below is a small explanation for each category:
  #     Feature: Commits related to implementing new features or functionalities in the project from the user perspective rather than extra classes or methods in code.
  #     BugFix: Commits addressing and fixing issues, bugs, or defects in the codebase.
  #     Refactor: Commits focused on improving code quality, organization, or structure without changing its external behavior.
  #     Support: Commits that help in increasing platform support in the future along with other commits.
  #     Installation: Commits that change the way a particular software in the repository is installed like the need to install some pre-required softwares or that software itself.
  #     Performance: Commits aimed at improving the performance of the codebase, such as optimizing algorithms, reducing resource usage, or enhancing execution speed.
  #     Dependency: Commits updating dependencies, importing any new libraries, or third-party components used in the project to newer versions.
  #     Tests: Commits related to adding, updating, or fixing tests to ensure code quality and reliability.
  #     TestSetup: Commits related to setting up test environments with some code snippet or a test setup for running the project
  #     Configuration: Commits updating configuration files, such as environment variables, build scripts, or project settings.
  #     Localization: Commits related to adding or updating translations, localization, or internationalization features in the project.
  #     Style: Commits focused on enforcing consistent code style, formatting, or coding conventions across the codebase.
  #     Chore: Commits related to general maintenance tasks, administrative work, or other miscellaneous changes that don't fit into other categories.
  #     Security: Commits addressing security vulnerabilities, implementing security measures, or ensuring compliance with security standards."""
  #   print(prompt)
  #   try:
  #     response = self.model.generate_content(prompt)
  #     commit_summary = response.text
  #   except:
  #     commit_summary = "Error in generating commit summary"

  #   # print("Commit summary: ", commit_summary)
  #   # print(f"\n\n\n\n\n\n commit : \n {commit_summary} ")
  #   return commit_summary
  
  def processing_new_commit(self, code_diff):
   
    prompt="""Based on the purpose of the code_diff,return what changes did the code_diff result into.
          ( NOTE: The '+' suggests the line is added into the code base and '-' suggests the line is removed from the code base. )
             say which category does the change in code_diff fall into amongst the following categories(or even closer to and if it doesnot belong to ayn category in the list,
           take it is under introduction and only give name of the category): Introduction ,Dependencies and requirements ,Installation steps
            ,Additional details ,Steps to use and examples of execution.
             For the given code_diff return the result as a dictionary with keys being 'Addition','Deletion','Updation'.Format as follows:
            {"Addition":<replace with Category>;<replace with description of change made and affected files or functionalities>  ,"Deletion":<replace with Category>;<replace with change made>  ,"Updation":<replace with Category>;<replace with change made>}.
            Here addition,deletion,updation refers to if the code changes made results in additional functionality or it results in removal of functionality or updation of functionality respectively.
            If there is no additional functionality or  removal of functionality or updation of functionality then assign the value of 'Addition','Deletion','Updation' keys accordingly to "None".
            Generate the result as discussed before for the code_diff given as follows:
           """
    response = self.model.generate_content(prompt + code_diff)
    return response.text
  
  def create_readem_summary(self,readme_sentences):
      prompt='''Based on the meaning of the line say which category does the line fall into
        amongst the following categories(or even closer to and if it doesnot belong to an category in the list, take it is under introduction and only give name of the category):
        Introduction ,Dependencies and requirements ,Installation steps ,Additional details ,Steps to use and examples of execution "
        '''
      response = self.model.generate_content(prompt + readme_sentences)
      return response.text.strip()
  
  def commit_summary_code_diff(self,commit_msg,file_summaries,FILE_SUMMARIES_BASED_ON_RAW_GIT_DIFF):
      file_summary=""
      file_summaries_diff=""
      for fn,fs in file_summaries:
        file_summary=file_summary+fn+" :\n"+fs+"\n"
      for fn,fs in FILE_SUMMARIES_BASED_ON_RAW_GIT_DIFF:
        file_summaries_diff=file_summaries_diff+fn+" :\n"+fs+"\n"
      prompt="""
        In a given commmit, the summaries of changes in files generated based on before and after files are gives as\n"""+file_summary+"""and the summaries based on only the raw git diffs is gives as\n"""+file_summaries_diff+""".
        The commit message given by the user for this commit is : """+commit_msg+""".
        Now based on both the summaries give commit summary in the structure [{<Action>:#Generalised summary#:$Project specific change$}]
        Square brackets contain the list of commit summaries inside with three tuples each,
        where Action, inside < >, can be something like Added, modified, removed, updated, fixed, changed, improved, refactored, enhanced, optimized, updated, upgraded, etc.
        Generalised, inside hases #, summary is a high level summary of changes from the perspective of a devloper along with the purpose or context of change,
        that can be generalised to any project without involving project specific details but not emitting important topics,
        so it can be used to classify the type of commit it is.
        Project specific, inside dollar sign $, change is the change that is specific to the project in which the commit is made.
        If the commit is related to a bug fix and also adds a new feature, then the commit summary can be like this:
        [{<Fixed>:#Auto Rotation of display#:$Fixed auto rotation issue in class Display by adding a new method rotateDisplay()$}
        {<Added>:#Setting up Configuration with api key#:$Requries OPEN_API_KEY to be set before running the test command$}]
        Example: [{<Fixed>:#Auto Rotation of display#:$Fixed auto rotation issue in class Display by adding a new method rotateDisplay()$}]
        Another example can be:[{<Addition>:#Setting up Configuration with api key#:$Requries OPEN_API_KEY to be set before running the test command$}]
        Another example can be:[{<Updated>:#Dependency Version for image processing#:$Updated the dependency version of image processing library from 1.0.0 to 1.1.0$}]
        Do not repeat the information in the Generalised summary and Project specific change or between Action and Generalised summary or between Generalised summary and Project specific change.
        For example don't say "[{<Added>: #Added State variables to the class#:$Added state variables to the class$}]".
        Instead say "[{<Added>: #Readme information on installation, setting up#: $Added OPEN_API_KEY key and bash script to set the model path$}]" 
        Need not repeat the action part verb like added, updated or fixed in remaning part of commit summary. 
        """
      # print(prompt)
      try:
        response = self.model.generate_content(prompt, safety_settings = [
          {
              "category": "HARM_CATEGORY_DANGEROUS",
              "threshold": "BLOCK_NONE",
          },
          {
              "category": "HARM_CATEGORY_HARASSMENT",
              "threshold": "BLOCK_NONE",
          },
          {
              "category": "HARM_CATEGORY_HATE_SPEECH",
              "threshold": "BLOCK_NONE",
          },
          {
              "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
              "threshold": "BLOCK_NONE",
          },
          {
              "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
              "threshold": "BLOCK_NONE",
          },
        ])
        commit_summary = response.text
      except(Exception) as e:
        print(e)
        commit_summary = "Error in generating commit summary"

      # print("Commit summary: ", commit_summary)
      # print(f"\n\n\n\n\n\n commit : \n {commit_summary} ")
      return commit_summary
      
    
