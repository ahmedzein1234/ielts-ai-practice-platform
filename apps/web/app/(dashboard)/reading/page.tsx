"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import {
  AlertCircle,
  ArrowLeft,
  ArrowRight,
  BookOpen,
  CheckCircle,
  Timer,
  XCircle
} from "lucide-react";
import { useEffect, useState } from "react";

interface Question {
  id: string;
  type: "multiple_choice" | "true_false" | "fill_blank" | "matching" | "summary_completion";
  question: string;
  options?: string[];
  correct_answer: string | string[];
  passage_section: number; // Which section of the passage this question relates to
  points: number;
}

interface ReadingPassage {
  id: string;
  title: string;
  content: string;
  word_count: number;
  difficulty: "easy" | "medium" | "hard";
  topic: string;
}

interface ReadingTest {
  id: string;
  title: string;
  description: string;
  duration: number; // in minutes
  difficulty: "easy" | "medium" | "hard";
  passages: ReadingPassage[];
  questions: Question[];
  band_score: number;
}

const mockReadingTest: ReadingTest = {
  id: "reading-001",
  title: "Academic Reading: Environmental Science",
  description: "Read three academic passages and answer questions about environmental science topics.",
  duration: 60,
  difficulty: "medium",
  band_score: 6.5,
  passages: [
    {
      id: "passage-1",
      title: "The Impact of Climate Change on Marine Ecosystems",
      content: `Climate change is having profound effects on marine ecosystems worldwide. Rising sea temperatures are causing coral bleaching, which occurs when corals expel the symbiotic algae that provide them with nutrients and their characteristic colors. This process leaves the coral white and vulnerable to disease.

The warming of ocean waters also affects the distribution of marine species. Many fish species are migrating to cooler waters, disrupting established food chains and fishing industries. For example, cod populations in the North Atlantic have moved northward by approximately 200 kilometers over the past 40 years.

Ocean acidification, caused by increased carbon dioxide absorption, is another significant threat. As CO2 dissolves in seawater, it forms carbonic acid, making the ocean more acidic. This affects organisms with calcium carbonate shells, such as mollusks and some plankton species, which struggle to form their protective structures in more acidic conditions.

The melting of polar ice caps is also contributing to sea level rise, which threatens coastal habitats and human settlements. Mangrove forests, salt marshes, and other coastal ecosystems that provide important nursery grounds for marine life are particularly vulnerable to these changes.`,
      word_count: 180,
      difficulty: "medium",
      topic: "Environmental Science"
    },
    {
      id: "passage-2",
      title: "Renewable Energy Technologies",
      content: `Renewable energy technologies have advanced significantly in recent decades, offering viable alternatives to fossil fuels. Solar power, once considered expensive and inefficient, has become one of the fastest-growing energy sources globally. The cost of solar panels has decreased by over 70% since 2010, making solar energy competitive with traditional power sources in many regions.

Wind energy has also experienced remarkable growth, particularly in coastal and high-altitude areas where wind speeds are consistently high. Modern wind turbines can generate electricity even at low wind speeds, and their efficiency has improved dramatically. Offshore wind farms, while more expensive to construct, can generate more power due to stronger and more consistent winds over the ocean.

Hydropower remains the largest renewable energy source globally, providing approximately 16% of the world's electricity. While large-scale hydroelectric dams can have significant environmental impacts, smaller run-of-river projects and pumped storage systems offer more sustainable alternatives.

Geothermal energy, which harnesses heat from the Earth's interior, is particularly promising in regions with high geothermal activity. Countries like Iceland and New Zealand have successfully integrated geothermal energy into their power grids, with geothermal sources providing up to 30% of their electricity needs.`,
      word_count: 165,
      difficulty: "medium",
      topic: "Technology"
    },
    {
      id: "passage-3",
      title: "Sustainable Agriculture Practices",
      content: `Sustainable agriculture practices are essential for feeding a growing global population while protecting the environment. Traditional farming methods often rely heavily on chemical fertilizers and pesticides, which can harm soil health and water quality. Sustainable alternatives focus on working with natural systems rather than against them.

Crop rotation is one of the oldest sustainable farming practices, involving the systematic planting of different crops in the same field over time. This practice helps maintain soil fertility, reduces pest populations, and improves soil structure. For example, planting legumes like beans or peas can naturally add nitrogen to the soil, reducing the need for synthetic fertilizers.

Integrated pest management (IPM) combines biological, cultural, and chemical methods to control pests while minimizing environmental impact. This approach includes using natural predators, crop diversification, and targeted pesticide application only when necessary. IPM has been shown to reduce pesticide use by 30-50% while maintaining crop yields.

Conservation tillage, which minimizes soil disturbance, helps prevent erosion and improves water retention. By leaving crop residues on the field and reducing plowing, farmers can protect soil from wind and water erosion while building organic matter content. This practice also reduces fuel consumption and greenhouse gas emissions from farm machinery.`,
      word_count: 170,
      difficulty: "medium",
      topic: "Agriculture"
    }
  ],
  questions: [
    {
      id: "q1",
      type: "multiple_choice",
      question: "What is coral bleaching?",
      options: [
        "A process where corals change color naturally",
        "A disease that affects coral reefs",
        "A process where corals expel symbiotic algae",
        "A method of coral conservation"
      ],
      correct_answer: "A process where corals expel symbiotic algae",
      passage_section: 1,
      points: 1
    },
    {
      id: "q2",
      type: "fill_blank",
      question: "Cod populations in the North Atlantic have moved northward by approximately _________ kilometers over the past 40 years.",
      correct_answer: "200",
      passage_section: 1,
      points: 1
    },
    {
      id: "q3",
      type: "true_false",
      question: "The cost of solar panels has increased since 2010.",
      correct_answer: "false",
      passage_section: 2,
      points: 1
    },
    {
      id: "q4",
      type: "multiple_choice",
      question: "Which renewable energy source provides the largest percentage of global electricity?",
      options: [
        "Solar power",
        "Wind energy",
        "Hydropower",
        "Geothermal energy"
      ],
      correct_answer: "Hydropower",
      passage_section: 2,
      points: 1
    },
    {
      id: "q5",
      type: "fill_blank",
      question: "Crop rotation helps maintain soil fertility and reduces _________ populations.",
      correct_answer: "pest",
      passage_section: 3,
      points: 1
    },
    {
      id: "q6",
      type: "true_false",
      question: "Integrated pest management can reduce pesticide use by 30-50%.",
      correct_answer: "true",
      passage_section: 3,
      points: 1
    }
  ]
};

export default function ReadingPage() {
  const [currentTest, setCurrentTest] = useState<ReadingTest>(mockReadingTest);
  const [currentPassage, setCurrentPassage] = useState(0);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string | string[]>>({});
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [score, setScore] = useState(0);
  const [timeRemaining, setTimeRemaining] = useState(currentTest.duration * 60);
  const [showPassage, setShowPassage] = useState(true);

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeRemaining((prev) => {
        if (prev <= 1) {
          handleSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const handleAnswerChange = (questionId: string, answer: string | string[]) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const handleSubmit = () => {
    let correctAnswers = 0;
    let totalPoints = 0;

    currentTest.questions.forEach(question => {
      const userAnswer = answers[question.id];
      const correctAnswer = question.correct_answer;

      if (userAnswer) {
        if (Array.isArray(correctAnswer)) {
          if (Array.isArray(userAnswer) &&
            userAnswer.length === correctAnswer.length &&
            userAnswer.every(ans => correctAnswer.includes(ans))) {
            correctAnswers++;
          }
        } else {
          if (Array.isArray(userAnswer)) {
            if (userAnswer.length === 1 && userAnswer[0].toLowerCase() === correctAnswer.toLowerCase()) {
              correctAnswers++;
            }
          } else if (userAnswer.toLowerCase() === correctAnswer.toLowerCase()) {
            correctAnswers++;
          }
        }
      }
      totalPoints += question.points;
    });

    const finalScore = (correctAnswers / currentTest.questions.length) * 9; // IELTS band score
    setScore(finalScore);
    setIsSubmitted(true);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case "easy": return "bg-green-100 text-green-800";
      case "medium": return "bg-yellow-100 text-yellow-800";
      case "hard": return "bg-red-100 text-red-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const getQuestionsForPassage = (passageIndex: number) => {
    return currentTest.questions.filter(q => q.passage_section === passageIndex + 1);
  };

  const currentPassageQuestions = getQuestionsForPassage(currentPassage);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Reading Test</h1>
        <p className="text-muted-foreground">Practice your reading comprehension with academic passages</p>
      </div>

      {/* Test Info */}
      <Card className="mb-6">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>{currentTest.title}</CardTitle>
              <CardDescription>{currentTest.description}</CardDescription>
            </div>
            <div className="flex items-center gap-4">
              <Badge className={getDifficultyColor(currentTest.difficulty)}>
                {currentTest.difficulty.charAt(0).toUpperCase() + currentTest.difficulty.slice(1)}
              </Badge>
              <div className="flex items-center gap-2">
                <Timer className="w-4 h-4" />
                <span>{formatTime(timeRemaining)}</span>
              </div>
            </div>
          </div>
        </CardHeader>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Passages */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <BookOpen className="w-5 h-5" />
                  Passages
                </CardTitle>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowPassage(!showPassage)}
                >
                  {showPassage ? "Hide" : "Show"} Passage
                </Button>
              </div>
              <div className="flex gap-2">
                {currentTest.passages.map((passage, index) => (
                  <Button
                    key={passage.id}
                    variant={currentPassage === index ? "default" : "outline"}
                    size="sm"
                    onClick={() => setCurrentPassage(index)}
                  >
                    Passage {index + 1}
                  </Button>
                ))}
              </div>
            </CardHeader>
            {showPassage && (
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <h3 className="text-lg font-semibold mb-2">
                      {currentTest.passages[currentPassage].title}
                    </h3>
                    <Badge variant="outline" className="mb-3">
                      {currentTest.passages[currentPassage].topic}
                    </Badge>
                    <div className="prose max-w-none">
                      <p className="text-gray-700 leading-relaxed whitespace-pre-line">
                        {currentTest.passages[currentPassage].content}
                      </p>
                    </div>
                    <p className="text-sm text-gray-500 mt-2">
                      Word count: {currentTest.passages[currentPassage].word_count}
                    </p>
                  </div>
                </div>
              </CardContent>
            )}
          </Card>
        </div>

        {/* Questions */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Questions</CardTitle>
              <CardDescription>
                Passage {currentPassage + 1} - Question {currentQuestion + 1} of {currentPassageQuestions.length}
              </CardDescription>
              <Progress
                value={(currentQuestion + 1) / currentPassageQuestions.length * 100}
                className="w-full"
              />
            </CardHeader>
            <CardContent>
              {currentPassageQuestions.map((question, index) => (
                <div
                  key={question.id}
                  className={`mb-8 p-4 rounded-lg border ${currentQuestion === index ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                    }`}
                >
                  <div className="flex items-start justify-between mb-4">
                    <h3 className="text-lg font-semibold">
                      Question {index + 1}
                    </h3>
                    <Badge variant="outline">
                      {question.type.replace('_', ' ').toUpperCase()}
                    </Badge>
                  </div>

                  <p className="mb-4 text-gray-700">{question.question}</p>

                  {question.type === "multiple_choice" && question.options && (
                    <div className="space-y-2">
                      {question.options.map((option, optionIndex) => (
                        <label
                          key={optionIndex}
                          className={`flex items-center p-3 rounded-lg border cursor-pointer transition-colors ${answers[question.id] === option
                              ? 'border-blue-500 bg-blue-50'
                              : 'border-gray-200 hover:border-gray-300'
                            }`}
                        >
                          <input
                            type="radio"
                            name={question.id}
                            value={option}
                            checked={answers[question.id] === option}
                            onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                            className="mr-3"
                            disabled={isSubmitted}
                          />
                          <span>{option}</span>
                          {isSubmitted && (
                            <div className="ml-auto">
                              {option === question.correct_answer ? (
                                <CheckCircle className="w-5 h-5 text-green-500" />
                              ) : answers[question.id] === option ? (
                                <XCircle className="w-5 h-5 text-red-500" />
                              ) : null}
                            </div>
                          )}
                        </label>
                      ))}
                    </div>
                  )}

                  {question.type === "fill_blank" && (
                    <input
                      type="text"
                      placeholder="Type your answer here..."
                      value={answers[question.id] as string || ""}
                      onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                      className="w-full p-3 border border-gray-300 rounded-lg"
                      disabled={isSubmitted}
                    />
                  )}

                  {question.type === "true_false" && (
                    <div className="space-y-2">
                      {["true", "false"].map((option) => (
                        <label
                          key={option}
                          className={`flex items-center p-3 rounded-lg border cursor-pointer transition-colors ${answers[question.id] === option
                              ? 'border-blue-500 bg-blue-50'
                              : 'border-gray-200 hover:border-gray-300'
                            }`}
                        >
                          <input
                            type="radio"
                            name={question.id}
                            value={option}
                            checked={answers[question.id] === option}
                            onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                            className="mr-3"
                            disabled={isSubmitted}
                          />
                          <span className="capitalize">{option}</span>
                          {isSubmitted && (
                            <div className="ml-auto">
                              {option === question.correct_answer ? (
                                <CheckCircle className="w-5 h-5 text-green-500" />
                              ) : answers[question.id] === option ? (
                                <XCircle className="w-5 h-5 text-red-500" />
                              ) : null}
                            </div>
                          )}
                        </label>
                      ))}
                    </div>
                  )}

                  {isSubmitted && (
                    <div className="mt-4 p-3 rounded-lg bg-gray-50">
                      <div className="flex items-center gap-2 mb-2">
                        <AlertCircle className="w-4 h-4 text-blue-500" />
                        <span className="font-semibold">Correct Answer:</span>
                      </div>
                      <p className="text-gray-700">
                        {Array.isArray(question.correct_answer)
                          ? question.correct_answer.join(", ")
                          : question.correct_answer
                        }
                      </p>
                    </div>
                  )}
                </div>
              ))}

              {/* Navigation */}
              <div className="flex items-center justify-between mt-6">
                <Button
                  variant="outline"
                  onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
                  disabled={currentQuestion === 0}
                >
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Previous
                </Button>

                <span className="text-sm text-gray-500">
                  {currentQuestion + 1} of {currentPassageQuestions.length}
                </span>

                <Button
                  variant="outline"
                  onClick={() => setCurrentQuestion(Math.min(currentPassageQuestions.length - 1, currentQuestion + 1))}
                  disabled={currentQuestion === currentPassageQuestions.length - 1}
                >
                  Next
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </div>

              {!isSubmitted && (
                <Button
                  onClick={handleSubmit}
                  className="w-full mt-4"
                  disabled={Object.keys(answers).length < currentTest.questions.length}
                >
                  Submit Test
                </Button>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Results Modal */}
      {isSubmitted && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle className="text-center">Test Results</CardTitle>
            </CardHeader>
            <CardContent className="text-center space-y-4">
              <div className="text-4xl font-bold text-blue-600">
                {score.toFixed(1)}
              </div>
              <p className="text-lg">Band Score</p>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-500">Correct Answers</p>
                  <p className="font-semibold">
                    {Object.keys(answers).filter(key => {
                      const question = currentTest.questions.find(q => q.id === key);
                      const answer = answers[key];
                      const correct = question?.correct_answer;

                      if (Array.isArray(correct)) {
                        return Array.isArray(answer) &&
                          answer.length === correct.length &&
                          answer.every(ans => correct.includes(ans));
                      }
                      if (Array.isArray(answer) || Array.isArray(correct)) {
                        return false;
                      }
                      return answer?.toLowerCase() === correct?.toLowerCase();
                    }).length} / {currentTest.questions.length}
                  </p>
                </div>
                <div>
                  <p className="text-gray-500">Time Used</p>
                  <p className="font-semibold">
                    {formatTime(currentTest.duration * 60 - timeRemaining)}
                  </p>
                </div>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={() => window.location.reload()}
                  className="flex-1"
                >
                  Retake Test
                </Button>
                <Button className="flex-1">
                  View Analysis
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
