document.addEventListener("DOMContentLoaded", function () {
    // 選取元素
    const leftArrow = document.getElementById("left-arrow");
    const rightArrow = document.getElementById("right-arrow");
    const searchDays = document.getElementById("search-days");

    // 初始化範圍
    let currentDays = parseInt(searchDays.textContent) || 3; // 儲存並讀取上次選擇的天數，如果沒有則默認為 3
    const minDays = 3;
    const maxDays = 7;

    // 更新文字與箭頭狀態
    function updateDays() {
        searchDays.textContent = `${currentDays}日遊`;
        localStorage.setItem("currentDays", currentDays); // 每次更新時將數字儲存

        // 左箭頭：若到達最小值則禁用
        if (currentDays === minDays) {
            leftArrow.disabled = true;
        } else {
            leftArrow.disabled = false;
        }

        // 右箭頭：若到達最大值則禁用
        if (currentDays === maxDays) {
            rightArrow.disabled = true;
        } else {
            rightArrow.disabled = false;
        }
    }

    // 點擊左箭頭
    leftArrow.addEventListener("click", function () {
        if (currentDays > minDays) {
            currentDays--;
            updateDays();
        }
    });

    // 點擊右箭頭
    rightArrow.addEventListener("click", function () {
        if (currentDays < maxDays) {
            currentDays++;
            updateDays();
        }
    });

    // 初始化顯示
    updateDays();
});

// 為每個帶有 .detail-button 類別的按鈕綁定點擊事件
const buttons = document.querySelectorAll(".detail-button");

buttons.forEach(button => {
    button.addEventListener("click", () => {
        // 導向到指定頁面
        window.location.href = "package.html";
    });
});
