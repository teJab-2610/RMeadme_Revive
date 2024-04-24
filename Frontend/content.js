import token from "./Keys.js";

let popupContent = null;
let copyreadme = null;
let wantsec = null;
let SuggestedData = null;
let lines_content_map = {};
function convertMarkdown(content) {
  const converter = new showdown.Converter();
  return converter.makeHtml(content);
}

function insertButton(button) {
  const readmeNavSection = findReadmeNavSection();
  const link = readmeNavSection.querySelector("a");

  if (link) {
    link.addEventListener("click", () => {
      markbuttoninactive(button);
      wantsec.innerHTML = copyreadme;
    });
  }

  if (readmeNavSection) {
    readmeNavSection.append(button);
  }

  button.addEventListener("click", () => {
    const url = window.location.href;
    const parts = url.split("/");
    const owner = parts[3];
    const repo = parts[4].split("?")[0];
    addStyletohead();
    fetchSuggestions(url)
    .then(() => fetchReadme(owner, repo))
    .then(() => markbuttonactive(button))
    .catch(error => console.error("Error fetching suggestions:", error));
  }
)};

function addStyletohead() {
  const head = document.head || document.getElementsByTagName("head")[0];
  const style = document.createElement("style");
  const css = `
  .dot {
    height: 10px;
    width: 10px;
    background-color: red;
    border-radius: 50%;
    display: inline-block;
    margin-right: 5px;
    cursor: pointer;
  }
  .popup-content {
    background-color: #f9f9f9;
    color: black;
    border: 1px solid #ccc;
    border-radius: 5px;
    padding: 2px;
    z-index: 5; 
    position: absolute; /* Added position */
  }
`;
  style.type = "text/css";
  if (style.styleSheet) {
    style.styleSheet.cssText = css;
  } else {
    style.appendChild(document.createTextNode(css));
  }
  head.appendChild(style);
}
function cleaned(text){
  //return all the chunks of text present in between dollar signs 
  const regex = /\$([^$]+)\$/g; // Regular expression to match text between dollar signs
    const matches = [];
    let match;
    while ((match = regex.exec(text)) !== null) {
        matches.push(match[1]); // Extract the text between dollar signs and add it to the array
    }
    return matches;
}
function fetchReadme(owner, repo) {
  const token = token;
  const apiUrl = `https://api.github.com/repos/${owner}/${repo}/readme`;
  console.log("Inside Fetch Readme")
  fetch(apiUrl, {
    headers: {
      Accept: "application/vnd.github+json",
      Authorization: `Bearer ${token}`,
      "X-GitHub-Api-Version": "2022-11-28",
    },
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
      const readmeContent = atob(data.content);
      const readmesec = findReadmeSection();
      for (let i = 0; i < SuggestedData.length; i++) {
        for (let j = 0; j < SuggestedData[i].lines.length; j++) {
          if(lines_content_map[SuggestedData[i].lines[j]]) {
            cleaned_text = cleaned(SuggestedData[i].summary);
            
            for (let k = 0; k < cleaned_text.length; k++) {
              lines_content_map[SuggestedData[i].lines[j]].push(cleaned_text[k]);
            }
          }
          else {
            cleaned_text = cleaned(SuggestedData[i].summary);
          
            lines_content_map[SuggestedData[i].lines[j]] = [cleaned_text[0]];
            for (let k = 1; k < cleaned_text.length; k++) {
              lines_content_map[SuggestedData[i].lines[j]].push(cleaned_text[k]);
            }
          }
        }
      }
      // console.log(lines_content_map);
      wantsec = readmesec;
      reqtodown = convertMarkdown(readmeContent);
      copyreadme = reqtodown;
      showdowncontent = parseReadmeContent(reqtodown);
      readmesec.innerHTML = showdowncontent;

      // Add event listeners to dots
      const dots = document.querySelectorAll(".dot");
      dots.forEach((dot) => {
        dot.addEventListener("mouseenter", (event) => {
          //get the id of the dot
          const dot_id = event.target.id;
          console.log(lines_content_map);
          showPopup(event, dot_id);
        });
        dot.addEventListener("mouseleave", () => {
          hidePopup();
        });
      });
    })
    .catch((error) => {
      console.error("Error fetching README:", error);
      const readmeDiv = document.getElementById("readme-content");
      readmeDiv.innerText = "Error fetching README.";
    });
}


function fetchSuggestions(url){
  return fetch("http://127.0.0.1:5000/process_repo", {
    method: "POST",
    body: JSON.stringify({ repo_url: url }),
    headers: {
      "Content-Type": "application/json",
    },
  })
  .then((response) => {
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }
    return response.json();
  })
  .then((data) => {
    // console.log(data);
    SuggestedData = data;
  })
  .catch((error) => {
    console.error("Error fetching suggestions:", error);
    // Optionally, return a default value or handle the error in another way
  });
}


function parseReadmeContent(content) {
  //split content based on newline character
  const lines = content.split("\n");
  parsedContent = "";
  for (let i = 0; i < lines.length; i++) {
    if (lines_content_map[i]) {
      parsedContent += `${lines[i]} <span class="dot" id="${i}"></span> \n`;
    } else {
      parsedContent += `${lines[i]} \n`;
    }
  }    
  // // Split the content by lines
  // let parsedContent = "";

  // // Process each line
  // // for (let i = 0; i < lines.length; i++) {
  // //   parsedContent += `${lines[i]} <span class="dot"></span> \n`;
  // // }
  // //after every </p> tag add a dot
  // parsedContent = content.replace(/<p>/g, '<p><span class="dot"></span>');
  return parsedContent;
}

function showPopup(event, idnum) {
  hidePopup(); // Hide existing popup if any

  let popupContentText = lines_content_map[idnum];

  // for(let i = 0; i < popupContentText.length; i++) {
  //   popupContentText[i] = `${popupContentText[i]}\n`;
  // }
  //Make them unlisted items
  popupContentText = popupContentText.join("\n");
  
  // Create and style the popup content
  popupContent = document.createElement("div");
  
  popupContent.classList.add("popup-content");
  popupContent.innerText = popupContentText;

  // Calculate position of popup content based on mouse coordinates and scroll offsets
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
  const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;

  popupContent.style.position = "absolute";
  popupContent.style.top = `${event.clientY + scrollTop}px`;
  popupContent.style.left = `${event.clientX + scrollLeft + 10}px`; // Adjust the offset from mouse pointer

  // Adjust popup content position if it exceeds the width of the viewport
  const popupWidth = popupContent.offsetWidth;
  const viewportWidth = window.innerWidth;

  if (event.clientX + popupWidth + 10 > viewportWidth) {
    popupContent.style.left = `${viewportWidth - popupWidth - 10}px`;
  }

  // Append popup content to the body
  document.body.appendChild(popupContent);
}

function hidePopup() {
  if (popupContent) {
    // Remove the popup content from the DOM
    popupContent.remove();
    popupContent = null;
  }
}

// Function to find the README section on GitHub

function findReadmeNavSection() {
  const readmeSections = document.querySelectorAll("ul");
  for (const section of readmeSections) {
    if (
      section.classList.contains("UnderlineNav__NavigationList-sc-1jfr31k-0")
    ) {
      return section;
    }
  }
  return null;
}

function findReadmeSection() {
  const readmeSections = document.querySelectorAll("article");
  for (const section of readmeSections) {
    if (section.classList.contains("markdown-body")) {
      return section;
    }
  }
  return null;
}

function markbuttonactive(button) {
  button.style.backgroundColor = "#1f883d"; // Adjust background color as needed
  //text color white
  button.style.color = "white"; // Adjust text color as needed
  icon.src =
    "https://raw.githubusercontent.com/AdityaAndaluri/MyFirstrepo/master/noborder.svg"; // Specify the path to your SVG icon
}

function markbuttoninactive(button) {
  button.style.backgroundColor = "white"; // Adjust background color as needed
  //text color white
  button.style.color = "black"; // Adjust text color as needed
  icon.src =
    "https://raw.githubusercontent.com/AdityaAndaluri/MyFirstrepo/master/rrimg.svg"; // Specify the path to your SVG icon
}

const icon = document.createElement("img");
icon.src =
  "https://raw.githubusercontent.com/AdityaAndaluri/MyFirstrepo/master/rrimg.svg"; // Specify the path to your SVG icon
icon.style.width = "15px"; // Adjust icon size as needed
//gap between icon and button text
icon.style.marginRight = "7px"; // Adjust gap between icon and button text as needed

// Create a button element
const button = document.createElement("button");
button.textContent = "REVIVE";
button.classList.add(
  "Box-sc-g0xbh4-0",
  "gwuIGu",
  "kOgeFj",
  "Link__StyledLink-sc-14289xe-0"
);
//add id to button
button.id = "myrevivebutton";
//button.style.marginTop = '10px'; // Adjust margin as needed
button.style.backgroundColor = "white"; // Adjust background color as needed
button.style.display = "inline"; // Adjust display as needed
button.style.border = "0px"; // Adjust border as needed
button.style.borderRadius = "5px"; // Adjust border radius as needed
button.style.color = "black"; // Adjust text color as needed
//padding between button text and border
button.style.padding = "5px"; // Adjust padding as needed
button.prepend(icon); // Insert the icon before the button text

// Find the README section

insertButton(button);

// Use MutationObserver to detect changes in the DOM and re-insert the button if necessary
const observer = new MutationObserver((mutationsList) => {
  for (const mutation of mutationsList) {
    if (mutation.type === "childList" && mutation.addedNodes.length) {
      // Check if the button is already present
      const existingButton = document.getElementById("myrevivebutton");
      if (!existingButton) {
        // If not, insert the button again
        insertButton(button);
      }
    }
  }
});

// Start observing changes in the body and its subtree
observer.observe(document.body, { subtree: true, childList: true });
