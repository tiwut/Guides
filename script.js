document.addEventListener('DOMContentLoaded', async () => {
    const guideListElement = document.getElementById('guideList');
    const searchInputElement = document.getElementById('searchInput');
    const statusMessageElement = document.getElementById('statusMessage');
    const languageSelector = document.getElementById('languageSelector');
    let allGuidesData = [];

    await i18next
        .use(i18nextBrowserLanguageDetector)
        .use(i18nextHttpBackend)
        .init({
            fallbackLng: 'en',
            debug: true,
            backend: {
                loadPath: 'locales/{{lng}}/translation.json'
            }
        });

    const updateContent = () => {
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            element.innerHTML = i18next.t(key);
        });
        document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
            const key = element.getAttribute('data-i18n-placeholder');
            element.placeholder = i18next.t(key);
        });
    };

    updateContent();
    languageSelector.value = i18next.language.split('-')[0];

    languageSelector.addEventListener('change', (e) => {
        i18next.changeLanguage(e.target.value, () => {
            updateContent();
            handleSearch();
        });
    });

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
                        en: parts[1].trim(),
                        de: parts[2].trim(),
                        es: parts[3].trim()
                    };
                })
                .filter(guide => guide !== null);

            if (allGuidesData.length > 0) {
                displayGuides(allGuidesData);
                statusMessageElement.textContent = '';
            } else {
                guideListElement.innerHTML = '';
                statusMessageElement.textContent = i18next.t('statusNoGuidesInFile');
            }
        } catch (error) {
            console.error('Error fetching or parsing guides.txt:', error);
            guideListElement.innerHTML = '';
            statusMessageElement.textContent = i18next.t('statusError', { message: error.message });
            if (window.location.protocol === "file:") {
                statusMessageElement.innerHTML += i18next.t('statusErrorFileProtocol');
            }
        }
    }

    function displayGuides(guidesToDisplay) {
        guideListElement.innerHTML = '';
        
        if (guidesToDisplay.length === 0 && searchInputElement.value.trim() !== '') {
            statusMessageElement.textContent = i18next.t('statusNoGuidesFound');
            statusMessageElement.style.display = 'block';
            return;
        } else if (guidesToDisplay.length === 0 && allGuidesData.length > 0) {
            statusMessageElement.textContent = i18next.t('statusNoGuidesFound');
            statusMessageElement.style.display = 'block';
            return;
        }
        
        statusMessageElement.style.display = 'none';

        guidesToDisplay.forEach((guideData, index) => {
            const listItem = document.createElement('li');
            const link = document.createElement('a');
            link.href = `./${guideData.folder}/`;

            const icon = document.createElement('img');
            icon.src = `./${guideData.folder}/main.avif`;
            icon.alt = `${guideData.folder} icon`;
            icon.onerror = function() {
                this.src = 'data:image/svg+xml;charset=UTF-8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23666"><path d="M21.99 4c0-1.1-.89-2-1.99-2H4c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2l-.01-16zM9 17l-3.5-3.5 1.41-1.41L9 14.17l6.09-6.09L16.5 9.5 9 17z"/></svg>';
                this.style.border = "1px solid #555";
                this.style.padding = "1px";
            };

            const nameSpan = document.createElement('span');
            nameSpan.className = 'guide-name';
            
            const currentLang = i18next.language.split('-')[0];
            nameSpan.textContent = guideData[currentLang] || guideData.en || guideData.folder;

            link.appendChild(icon);
            link.appendChild(nameSpan);
            listItem.appendChild(link);
            
            listItem.classList.add('list-item-animate');
            listItem.style.animationDelay = `${index * 50}ms`;

            guideListElement.appendChild(listItem);
        });
    }

    function handleSearch() {
        const searchTerm = searchInputElement.value.toLowerCase().trim();
        if (!allGuidesData || allGuidesData.length === 0) {
            if (statusMessageElement.textContent === '') {
                statusMessageElement.textContent = i18next.t('statusGuidesNotLoaded');
                statusMessageElement.style.display = 'block';
            }
            return;
        }
        
        const filteredGuides = allGuidesData.filter(guide => {
            return guide.en.toLowerCase().includes(searchTerm) ||
                   guide.de.toLowerCase().includes(searchTerm) ||
                   guide.es.toLowerCase().includes(searchTerm);
        });

        displayGuides(filteredGuides);
    }

    await loadGuides();

    searchInputElement.addEventListener('input', handleSearch);
});