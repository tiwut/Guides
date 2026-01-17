document.addEventListener('DOMContentLoaded', async () => {
    const guideListElement = document.getElementById('guideList');
    const searchInputElement = document.getElementById('searchInput');
    const statusMessageElement = document.getElementById('statusMessage');
    let allGuidesData = [];

    async function loadGuides() {
        try {
            const response = await fetch('guides.txt');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status} - Could not load guides.txt`);
            }
            const text = await response.text();

            allGuidesData = text.split('\n')
                .map(line => line.trim())
                .filter(line => line)
                .map(line => {
                    const parts = line.split(';');
                    if (parts.length < 4) {
                        console.warn(`Skipping malformed line in guides.txt: ${line}`);
                        return null;
                    }
                    return {
                        folder: parts[0].trim(),
                        name: parts[1].trim()
                    };
                })
                .filter(guide => guide !== null);

            if (allGuidesData.length > 0) {
                displayGuides(allGuidesData);
                statusMessageElement.textContent = '';
            } else {
                guideListElement.innerHTML = '';
                statusMessageElement.textContent = 'No guides found in the file.';
            }
        } catch (error) {
            console.error('Error fetching or parsing guides.txt:', error);
            guideListElement.innerHTML = '';
            statusMessageElement.textContent = `Error loading guides: ${error.message}`;
            if (window.location.protocol === "file:") {
                statusMessageElement.innerHTML += '<br><strong>Note:</strong> Browsers block fetching local files via AJAX (CORS). Please run this via a local server (e.g., VS Code Live Server, Python http.server, etc.) or check your browser console.';
            }
        }
    }

    function displayGuides(guidesToDisplay) {
        guideListElement.innerHTML = '';

        if (guidesToDisplay.length === 0 && searchInputElement.value.trim() !== '') {
            statusMessageElement.textContent = 'No matching guides found.';
            statusMessageElement.style.display = 'block';
            return;
        } else if (guidesToDisplay.length === 0 && allGuidesData.length > 0) {
            statusMessageElement.textContent = 'No guides available.';
            statusMessageElement.style.display = 'block';
            return;
        }

        statusMessageElement.style.display = 'none';

        guidesToDisplay.forEach((guideData, index) => {
            const listItem = document.createElement('li');
            const link = document.createElement('a');
            link.href = `./${guideData.folder}/`;

            link.addEventListener('click', (e) => {
                e.preventDefault();
                document.body.classList.add('page-exit-active');
                setTimeout(() => {
                    window.location.href = link.href;
                }, 400);
            });

            const nameSpan = document.createElement('span');
            nameSpan.className = 'guide-name';
            nameSpan.textContent = guideData.name;

            link.appendChild(nameSpan);
            listItem.appendChild(link);

            listItem.classList.add('list-item-animate');
            listItem.style.animationDelay = `${index * 30}ms`;

            if (window.applyGuideMagnetic) {
                window.applyGuideMagnetic(listItem);
            }

            guideListElement.appendChild(listItem);
        });
    }

    function handleSearch() {
        const searchTerm = searchInputElement.value.toLowerCase().trim();
        if (!allGuidesData || allGuidesData.length === 0) {
            if (statusMessageElement.textContent === '') {
                statusMessageElement.textContent = 'Guides are not loaded yet.';
                statusMessageElement.style.display = 'block';
            }
            return;
        }

        const filteredGuides = allGuidesData.filter(guide => {
            return guide.name.toLowerCase().includes(searchTerm);
        });

        displayGuides(filteredGuides);
    }

    window.addEventListener('pageshow', (event) => {
        if (document.body.classList.contains('page-exit-active')) {
            document.body.classList.remove('page-exit-active');
            document.body.classList.add('page-enter-active');

            setTimeout(() => {
                document.body.classList.remove('page-enter-active');
            }, 500);
        }
    });

    if (guideListElement) {
        await loadGuides();
        searchInputElement.addEventListener('input', handleSearch);
    }

    function applyMagneticEffect(element, strength = 0.5) {
        element.addEventListener('mousemove', (e) => {
            const rect = element.getBoundingClientRect();
            const x = e.clientX - (rect.left + rect.width / 2);
            const y = e.clientY - (rect.top + rect.height / 2);

            element.style.setProperty('--mag-x', `${x * strength}px`);
            element.style.setProperty('--mag-y', `${y * strength}px`);
            element.classList.add('is-magnetic-hover');
        });

        element.addEventListener('mouseleave', () => {
            element.style.removeProperty('--mag-x');
            element.style.removeProperty('--mag-y');
            element.classList.remove('is-magnetic-hover');
        });
    }

    const mainPageButtons = document.querySelectorAll('.main-page-button, button, #languageSelector');
    mainPageButtons.forEach(el => applyMagneticEffect(el, 0.3));

    const sidebarLinks = document.querySelectorAll('#sidebar ul li a');
    sidebarLinks.forEach((el, index) => {
        applyMagneticEffect(el, 0.2);

        el.style.opacity = '0';
        el.style.animation = `textCreation 0.5s ease-out forwards ${index * 50}ms`;
    });

    window.applyGuideMagnetic = function (li) {
        applyMagneticEffect(li, 0.15);
    };

    if (document.querySelectorAll('#guideList li').length > 0) {
        document.querySelectorAll('#guideList li').forEach(li => window.applyGuideMagnetic(li));
    }
});