import { Component, ViewChild, Input } from '@angular/core';
import { NavController} from 'ionic-angular';
import chartJs from 'chart.js';

import { UserService } from '../../providers/util/user.service';
import { ToastService } from '../../providers/util/toast.service';

@Component({
  selector: 'graph',
  templateUrl: 'graph.html'
})
export class GraphComponent {

  @Input() data;
  @ViewChild('barCanvas') barCanvas;

  barChart: any;

  constructor(public navCtrl: NavController, 
    public userService: UserService,
    public toastService: ToastService) { }

  ngAfterViewInit() {
    setTimeout(() => {
      this.barChart = this.getBarChart();
    }, 150);

  }

  getChart(context, chartType, data, options?) {
    return new chartJs(context, {
      data,
      options,
      type: chartType,
    });
  }

  getBarChart() {

    const labels = [];
    const scores = [];
    for (const username in this.data['scores']) {
      labels.push(username);
      scores.push(this.data['scores'][username]);
    }
    const barData = {
      'labels': labels,
      data: scores,
      borderWidth: 1
    };

    const options = {
      scales: {
        yAxes: [{
          ticks: {
            beginAtZero: true
          }
        }]
      }
    };

    return this.getChart(this.barCanvas.nativeElement, 'bar', barData, options);
  }
}

