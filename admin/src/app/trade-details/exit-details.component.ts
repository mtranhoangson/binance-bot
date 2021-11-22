import {Component, Input, OnInit} from '@angular/core';
import {Mode, Target, TradeDetails} from '../trade-details';

@Component({
  selector: 'app-exit-details',
  templateUrl: './exit-details.component.html',
  styleUrls: ['./trade-details.component.css']
})

export class ExitDetailsComponent implements OnInit {
  @Input()
  trade: TradeDetails;

  @Input()
  mode: Mode;

  lastAddedTarget: Target;

  constructor() {

  }

  ngOnInit(): void {
  }

  deleteTarget(exitTarget: Target) {
    if (exitTarget === this.lastAddedTarget) {
      this.lastAddedTarget = null;
    }
    this.trade.exit.targets = this.trade.exit.targets.filter(et => et !== exitTarget);
  }

  addNewTarget() {
    if (this.lastAddedTarget && !this.lastAddedTarget.price) { return; }

    this.lastAddedTarget = new Target();

    if (!this.trade.exit.targets){
      this.trade.exit.targets = [];
    }
    this.trade.exit.targets.push(this.lastAddedTarget);
  }
}
