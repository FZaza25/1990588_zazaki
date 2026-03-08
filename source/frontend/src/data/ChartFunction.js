export function computeTime(array){
    let timeLabel = []
    for(let i=1; i<=array.length; i++){
        timeLabel.push(i*5)
    }
    return timeLabel
}