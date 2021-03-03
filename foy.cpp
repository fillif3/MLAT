// MathLibrary.cpp : Defines the exported functions for the DLL.
#include "pch.h" // use stdafx.h in Visual Studio 2017 and earlier
#include <utility>
#include <limits.h>
#include "foy.h"
#include "geodetic.h"
#include <fstream>
#include <string>

#include <iostream>
#include <Eigen/Dense>

using namespace std;

int test(int a, int b)
{
    int c = a + b;
    return c;
}


Eigen::Vector3f correct_z(const float lat_reference, const float long_reference,
    const float alt_reference, const float height, Eigen::Vector3f position)
{
    geodetic_converter::GeodeticConverter g_geodetic_converter;
    g_geodetic_converter.initialiseReference(lat_reference, long_reference, alt_reference);
    double lat, lon, alt, east, north, up;
    g_geodetic_converter.enu2Geodetic(position(0), position(1), position(2), &lat, &lon, &alt);
    g_geodetic_converter.geodetic2Enu(lat, lon, height, &east, &north, &up);
    position(0) = east;
    position(1) = north;
    position(2) = up;
    return position;

}


Eigen::VectorXf compute_errors(Eigen::MatrixXf anchors, Eigen::VectorXf ranges,
    Eigen::Vector3f position)
{
    int number_of_ranges = ranges.size();
    Eigen::VectorXf difference_of_ranges(number_of_ranges - 1);
    for (int i = 0;i < (number_of_ranges - 1);i++)
    {
        difference_of_ranges(i) = ranges(i) - ranges(number_of_ranges - 1);
    }
    Eigen::VectorXf computed_difference_of_ranges(number_of_ranges - 1);
    Eigen::Vector3f reference_anchor(3);
    Eigen::Vector3f current_anchor(3);
    reference_anchor(0) = anchors(number_of_ranges - 1, 0);
    reference_anchor(1) = anchors(number_of_ranges - 1, 1);
    reference_anchor(2) = anchors(number_of_ranges - 1, 2);
    float reference_range = (reference_anchor - position).norm();
    for (int i = 0;i < (number_of_ranges - 1);i++)
    {
        current_anchor(0) = anchors(i, 0);
        current_anchor(1) = anchors(i, 1);
        current_anchor(2) = anchors(i, 2);
        computed_difference_of_ranges(i) = (current_anchor - position).norm() - reference_range;
    }
    Eigen::VectorXf errors = difference_of_ranges - computed_difference_of_ranges;
    return errors;
}

Eigen::MatrixXf compute_jacobian2_5D(Eigen::MatrixXf anchors, Eigen::Vector3f position)
{
    int number_of_anchors = anchors.size() / 3;
    Eigen::MatrixXf Jacobian(number_of_anchors - 1, 2);
    //cout << Jacobian << endl;
    Eigen::Vector3f reference_anchor(3);
    //cout << reference_anchor << endl;
    reference_anchor(0) = anchors(number_of_anchors - 1, 0);
    reference_anchor(1) = anchors(number_of_anchors - 1, 1);
    reference_anchor(2) = anchors(number_of_anchors - 1, 2);
    //cout << reference_anchor << endl;

    float dist_to_reference = reference_anchor.norm();
    //cout << dist_to_reference << endl;
    Eigen::Vector3f refence_derievative = position - reference_anchor;
    //cout << refence_derievative << endl;
    refence_derievative /= dist_to_reference;
    //cout << refence_derievative << endl;
    Eigen::Vector3f current_anchor(3);
    float dist_to_current_anchor;
    Eigen::Vector3f current_derievative;

    for (int i = 0;i < (number_of_anchors - 1);i++)
    {
        current_anchor(0) = anchors(i, 0);
        current_anchor(1) = anchors(i, 1);
        current_anchor(2) = anchors(i, 2);
        //cout << current_anchor << endl;
        dist_to_current_anchor = (current_anchor - position).norm();
        //cout << dist_to_current_anchor << endl;
        current_derievative = (position - current_anchor);
        //cout << current_derievative << endl;

        current_derievative /= dist_to_current_anchor;
        //cout << current_derievative << endl;
        for (int j = 0;j < 2;j++)
        {
            Jacobian(i, j) = current_derievative(j) - refence_derievative(j);
            //cout << Jacobian << endl;
        }
    }/**/
    return Jacobian;
}

int foy(float anchors_list[], int number_of_anchors,float ranges_list[], const float height,
    const float lat_reference, const float long_reference, const float alt_reference,
    const float starting_east, const float starting_north, const float starting_up,
    float* lat_position, float* long_position, float* alt_position, int* iterations)
{
    //std::ofstream file("C:/Intel/etxt");
    //std::string my_string = "starte\n";
    //file << my_string;
    //cout << "I'm here" << endl;
    Eigen::MatrixXf anchors(number_of_anchors,3);
    Eigen::VectorXf ranges(number_of_anchors);
    //file << my_string;
    for (int i=0;i<number_of_anchors;i++)
    {
        anchors(i, 0) = anchors_list[i * 3];
        anchors(i, 1) = anchors_list[i * 3+1];
        anchors(i, 2) = anchors_list[i * 3+2];
        ranges(i) = ranges_list[i];
    }
    //file << my_string;
    Eigen::Vector3f reference(starting_east, starting_north, starting_up);
    float tresh = 1000;
    int i;

    for (i = 0;i < 50000;i++)
    {
        //my_string = "loop started \n";
        //file << my_string;
        Eigen::MatrixXf A = compute_jacobian2_5D(anchors, reference);
        //file << my_string;
        //cout << A << endl << endl;
        Eigen::VectorXf errors = compute_errors(anchors, ranges, reference);
        //file << my_string;
        //cout << errors << endl << endl;
        Eigen::MatrixXf A_tran = A.transpose();
        //my_string = "starting algebra";
        //file << my_string;
        //cout << A_tran << endl << endl;
        Eigen::MatrixXf helper = A_tran * A;
        //cout << helper << endl << endl;
        //file << my_string;

        try
        {
            helper = helper.inverse();
        }
        catch (...) {
            // Catch all exceptions - dangerous!!!
            // Respond (perhaps only partially) to the exception, then
            // re-throw to pass the exception to some other handler
            // ...
            break;
        }
        //cout << helper << endl << endl;
        //file << my_string;
        Eigen::Vector2f delta = helper * A_tran * errors; //Dodać try catch
        //cout << delta << endl;
        //file << my_string;
        Eigen::Vector3f estimator_next = reference;
        //cout << delta << endl;
        estimator_next(0) += delta(0);
        estimator_next(1) += delta(1);
        //my_string = "computing altitude\n";
        //file << my_string;
        //cout << estimator_next << endl;
        estimator_next =
            correct_z(lat_reference, long_reference, alt_reference, height, estimator_next);
        //cout << estimator_next << endl;
        //file << my_string;
        Eigen::VectorXf errors_next = compute_errors(anchors, ranges, estimator_next);
        //cout << errors_next << endl;
        if ((i < 3) || (errors_next.norm() < errors.norm()))
        {
            reference = estimator_next;
        }
        else
        {

            break;
        }


    }

    //my_string = "writing refernces\n";
    //file << my_string;
    *lat_position = reference(0);

    //file << my_string;
    *long_position = reference(1);

    //file << my_string;
    *alt_position = reference(2);
    //file << my_string;
    *iterations = i;
    //my_string = "koniec";
    //file << my_string;
    return 9;
}

