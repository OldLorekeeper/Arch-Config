const paper = require('paper');

paper.setup(new paper.Size(200, 200));

const clipPathData = "M63.09 37c14.626-25.333 51.193-25.334 65.819 0l45.033 78c14.626 25.334-3.657 57.001-32.91 57.001H50.967c-29.253 0-47.536-31.667-32.91-57.001z";
const yellowData = "M206.905 172.02h-91.888l-19.015-32.934 45.944-79.578z";
const blueData = "M-14.919 172.006 50.04 59.494v.002L31.032 92.422h38.02L115 172.004l-129.918.001z";
const greenData = "M96.007-20.085 141.954 59.5l-19.011 32.928H31.048z";

const clipPath = new paper.Path(clipPathData);
const yellowPath = new paper.Path(yellowData);
const bluePath = new paper.Path(blueData);
const greenPath = new paper.Path(greenData);

const yInt = yellowPath.intersect(clipPath);
const bInt = bluePath.intersect(clipPath);
const gInt = greenPath.intersect(clipPath);

console.log("YELLOW:" + yInt.pathData);
console.log("BLUE:" + bInt.pathData);
console.log("GREEN:" + gInt.pathData);
