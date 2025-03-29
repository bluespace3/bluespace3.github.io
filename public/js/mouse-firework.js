// 鼠标烟花效果脚本
// 从CDN加载mouse-firework库
document.addEventListener('DOMContentLoaded', function() {
  // 创建script元素
  const script = document.createElement('script');
  script.src = 'https://npm.webcache.cn/mouse-firework@0.1.0/dist/index.umd.js';
  script.integrity = 'sha384-KM6i7tu43nYd6e0beIljxHMC5tZc58XBDu7pPA58w50h18Jsx7gLdimfS09RXlKv';
  script.crossOrigin = 'anonymous';
  
  // 脚本加载完成后初始化烟花效果
  script.onload = function() {
    if (window.firework) {
      const options = {
        excludeElements: ["a", "button"],
        particles: [
          {
            shape: "circle",
            move: ["emit"],
            easing: "easeOutExpo",
            colors: ["#5252ff", "#7c7cff", "#afafff", "#d0d0ff"],
            number: 20,
            duration: [1200, 1800],
            shapeOptions: {
              radius: [16, 32],
              alpha: [0.3, 0.5]
            }
          },
          {
            shape: "circle",
            move: ["diffuse"],
            easing: "easeOutExpo",
            colors: ["#0000ff"],
            number: 1,
            duration: [1200, 1800],
            shapeOptions: {
              radius: 20,
              alpha: [0.2, 0.5],
              lineWidth: 6
            }
          }
        ]
      };
      window.firework(options);
    }
  };
  
  // 添加到文档中
  document.body.appendChild(script);
});