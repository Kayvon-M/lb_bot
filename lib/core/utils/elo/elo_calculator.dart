import 'dart:math';

class EloCalculator {
  static const double k = 75.0;

  static double expectedScore(double rating1, double rating2) {
    return 1.0 / (1.0 + pow(10.0, (rating2 - rating1) / 400.0));
  }

  static double newRating(
      double rating, double expectedScore, double actualScore) {
    return rating + k * (actualScore - expectedScore);
  }

  static double newRatingFromScores(
      double rating, double opponentRating, double score) {
    return newRating(rating, expectedScore(rating, opponentRating), score);
  }
}
