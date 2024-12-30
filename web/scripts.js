// DOM 載入後執行
document.addEventListener("DOMContentLoaded", function () {
    // 選取元素
    const leftArrow = document.getElementById("left-arrow");
    const rightArrow = document.getElementById("right-arrow");
    const searchDays = document.getElementById("search-days");

    // 初始化範圍
    let currentDays = 3; // 起始為三日遊
    const minDays = 3;
    const maxDays = 7;

    // 更新文字與箭頭狀態
    function updateDays() {
        searchDays.textContent = `${currentDays}日遊`;

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
