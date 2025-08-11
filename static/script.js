document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Element References ---
    const topicInput = document.getElementById('topic-input');
    const generateBtn = document.getElementById('generate-btn');
    const autonomousBtn = document.getElementById('autonomous-btn');
    const loadingIndicator = document.getElementById('loading-indicator');
    const errorMessage = document.getElementById('error-message');

    const chapterContent = document.getElementById('chapter-content');
    const relationsState = document.getElementById('relations-state');
    const memoryState = document.getElementById('memory-state');

    // --- Utility Functions ---
    const showLoading = (isLoading) => {
        loadingIndicator.classList.toggle('hidden', !isLoading);
        generateBtn.disabled = isLoading;
    };

    const showError = (message) => {
        errorMessage.textContent = message;
        errorMessage.classList.remove('hidden');
    };

    const hideError = () => {
        errorMessage.classList.add('hidden');
    };

    const updateStateDisplays = (state) => {
        relationsState.textContent = JSON.stringify(state.relations, null, 2);
        memoryState.textContent = JSON.stringify(state.memory, null, 2);
    };

    // --- API Communication ---
    const fetchInitialState = async () => {
        try {
            const response = await fetch('/state');
            if (!response.ok) {
                throw new Error(`无法加载初始状态: ${response.statusText}`);
            }
            const state = await response.json();
            updateStateDisplays(state);
        } catch (error) {
            showError(error.message);
        }
    };

    const generateNewChapter = async () => {
        const topic = topicInput.value.trim();
        if (!topic) {
            showError('请输入一个故事主题。');
            return;
        }

        hideError();
        showLoading(true);

        try {
            const response = await fetch('/chapter', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ topic: topic }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || '生成章节时发生未知错误。');
            }

            const data = await response.json();

            // 更新章节内容
            const chapterHtml = `<h3>${data.chapter}</h3><p>${data.content.replace(/\n/g, '<br>')}</p>`;
            chapterContent.innerHTML = chapterHtml;

            // 更新状态显示
            updateStateDisplays({
                relations: data.relationship_map,
                memory: data.memory_updates // 注意：这里只显示了最新的更新，可以调整为获取完整记忆
            });

            // 获取并显示完整状态
            await fetchInitialState();


        } catch (error) {
            showError(`请求失败: ${error.message}`);
        } finally {
            showLoading(false);
        }
    };

    const runAutonomousStep = async () => {
        hideError();
        showLoading(true);

        try {
            const response = await fetch('/autonomous_step', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || '自主生成章节时发生未知错误。');
            }

            const data = await response.json();

            // Clear the manual input box as we are in auto mode
            topicInput.value = '';

            const chapterHtml = `<h3>${data.chapter}</h3><p>${data.content.replace(/\n/g, '<br>')}</p>`;
            chapterContent.innerHTML = chapterHtml;

            await fetchInitialState();

        } catch (error) {
            showError(`请求失败: ${error.message}`);
        } finally {
            showLoading(false);
        }
    };

    // --- Event Listeners ---
    generateBtn.addEventListener('click', generateNewChapter);
    autonomousBtn.addEventListener('click', runAutonomousStep);

    // --- Initial Load ---
    fetchInitialState();
});
