
var CHART = { 'title' : 'untitled' };

function getValue(id)
{
    return document.getElementById(id).value;
};

function runSim(pid)
{     
    $('run').disabled = true;
    CHART.title = getValue('project');
            
    var resultsURL = sprintf("/project/%d/results?trials=", pid) + $('trials').value;
    var jsonRequest = new Request.JSON({method: 'get', url: resultsURL, onSuccess: showResults});
    document.body.style.cursor = "wait";
    jsonRequest.get();
};

function exportSim(pid)
{                 
    var resultsURL = sprintf("/project/%d/resultscsv?trials=", pid) + $('trials').value;
    //alert(resultsURL);
    window.location.href = resultsURL;
};

function taskSim(row)
{                
    var type = getValue('type');
    
    var title = getValue("desc_" + row);
    var count = getValue("count_" + row);
    var median = getValue("median_" + row);
    var risk = getValue("risk_" + row);
    var resultsURL = sprintf("/montecarlo?trials=10000&count=%s&estimate=%s&risk=%s&type=%s", count, median, risk, type);
    
    CHART.title = title;
    
    var jsonRequest = new Request.JSON({method: 'get', url: resultsURL, onSuccess: showResults});
    document.body.style.cursor = "wait";
    jsonRequest.get();
};

function riskSim(risk)
{               
    var type = getValue('type');
    var resultsURL = sprintf("/montecarlo?trials=10000&count=1&estimate=10&risk=%s&type=%s", risk, type);
    
    CHART.title = sprintf("risk=%s for %s=10", risk, type);
    
    var jsonRequest = new Request.JSON({method: 'get', url: resultsURL, onSuccess: showResults});
    document.body.style.cursor = "wait";
    jsonRequest.get();
};

function showResults(results)
{
    $('trials').value = results.trials;
            
    $('result').innerHTML = sprintf("Monte Carlo simulation took %3.2fs for %d iterations", results.simtime, results.trials);
    $('nominal').innerHTML = sprintf("%.2f", results.nominal);
    $('mean').innerHTML = sprintf("%.2f", results.mean);
    $('mode').innerHTML = sprintf("%.2f", results.mode);
    $('p10').innerHTML = sprintf("%.2f", results.cumprob[10][0]);
    $('p50').innerHTML = sprintf("%.2f", results.cumprob[50][0]);
    $('p80').innerHTML = sprintf("%.2f", results.cumprob[80][0]); 
    $('p90').innerHTML = sprintf("%.2f", results.cumprob[90][0]);  
    $('p95').innerHTML = sprintf("%.2f", results.cumprob[95][0]);  
    $('p99').innerHTML = sprintf("%.2f", results.cumprob[99][0]);  
    $('ratio9010').innerHTML = sprintf("%.2f", results.cumprob[90][0]/results.cumprob[10][0]); 
    $('ratio9050').innerHTML = sprintf("%.2f", results.cumprob[90][0]/results.cumprob[50][0]);  
    $('risk').innerHTML = sprintf("%.2f", results.risk);  
    $('pnom').innerHTML = sprintf("%.2f", results.pnom);
    
    drawChart(results.cumprob);
    $('run').disabled = false;
    document.body.style.cursor = "default";
};

function drawChart(myData)
{
    var myChart = new JSChart('graph', 'line');
    myChart.setDataArray(myData);
    myChart.setLineColor('#8D9386');
    myChart.setLineWidth(4);
    myChart.setTitleColor('#7D7D7D');
    myChart.setAxisColor('#9F0505');
    myChart.setGridColor('#a4a4a4');
    myChart.setAxisValuesColor('#333639');
    myChart.setAxisNameColor('#333639');
    myChart.setTextPaddingLeft(0);
    myChart.setAxisNameX(sprintf("Effort (%s)", $('units').value));
    myChart.setAxisNameY("Confidence");
    myChart.setTitle(CHART.title);
    myChart.draw();
};

function toggleLegend()
{
    if ($('legend').style.display == 'block')
    {
        $('toggler').innerHTML = 'show risk legend';
        $('legend').style.display = 'none';
    }
    else
    {
        $('toggler').innerHTML = 'hide risk legend';
        $('legend').style.display = 'block';
    }
}
