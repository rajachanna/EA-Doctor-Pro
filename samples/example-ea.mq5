// Synthetic sample for diagnostic unit tests. NOT A LIVE TRADING STRATEGY.
#property strict
#include <Trade/Trade.mqh>
CTrade trade;
input double Lots=0.10;

void OnTick() {
    trade.Buy(Lots, _Symbol);
}
